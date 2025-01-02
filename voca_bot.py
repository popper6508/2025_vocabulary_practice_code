import pandas as pd
import random
from flask import Flask, render_template, request
from bs4 import BeautifulSoup as bs
import requests

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def vocabulary():
    excel_file = "vocabulary.xlsx"
    df = pd.read_excel(excel_file)

    start = None
    end = None
    selected_row = None
    meaning = ""
    sentence = ""
    correct_answer = None
    feedback = None
    user_input = None
    show_answer = None

    if request.method == "POST":
        start = int(request.form.get("start") or 0)
        end = int(request.form.get("end") or len(df) - 1)

        start = max(0, start)
        end = min(len(df) - 1, end)

        if "next" in request.form:
            selected_row = random.randint(start, end)
            row_data = df.iloc[selected_row]
            correct_answer = row_data["Answer"]
            meaning = row_data["Meaning"].replace(correct_answer, "_____")
            sentence = row_data["Sentences"].replace(correct_answer, "_____")

        elif "check_answer" in request.form:
            if "word" in request.form:
                user_input = request.form.get("word").strip().lower()
                selected_row = int(request.form.get("selected_row"))
                row_data = df.iloc[selected_row]
                correct_answer = row_data["Answer"]
                meaning = row_data["Meaning"].replace(correct_answer, "_____")
                sentence = row_data["Sentences"].replace(correct_answer, "_____")
                feedback = "Correct!" if user_input == correct_answer.lower() else "Try again!"

        elif "show_answer" in request.form:
            selected_row = int(request.form.get("selected_row"))
            row_data = df.iloc[selected_row]
            correct_answer = row_data["Answer"]
            meaning = row_data["Meaning"].replace(correct_answer, "_____")
            sentence = row_data["Sentences"].replace(correct_answer, "_____")
            show_answer = correct_answer

    return render_template(
        "voca_prac.html",
        meaning_lines=split_into_lines(meaning),
        sentence_lines=split_into_lines(sentence),
        correct_answer=correct_answer,
        feedback=feedback,
        user_input=user_input,
        show_answer=show_answer,
        start=start,
        end=end,
        selected_row=selected_row,
        df=df[['No', 'Meaning', 'Answer']].to_html(classes="table table-striped", index=False),
    )


@app.route("/add", methods=["GET", "POST"])
def add_vocabulary():
    excel_file = "vocabulary.xlsx"
    original_df = pd.read_excel(excel_file)
    original_row_count = len(original_df)
    message = None
    error = None

    if request.method == "POST":
        if "add_word" in request.form:
            new_word = request.form.get("word").strip().lower()

            url = f"https://dictionary.cambridge.org/dictionary/english/{new_word}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = bs(response.text, 'html.parser')

                word_definitions = soup.find_all(class_="def ddef_d db")
                definitions = [definition.text.strip() for definition in word_definitions]

                word_sentences = soup.find_all(class_="deg")
                sentences = [sentence.text.strip() for sentence in word_sentences]

                next_number = original_row_count + 1

                new_row = {
                    "No": next_number,
                    "Meaning": "\n".join(definitions),
                    "Answer": new_word,
                    "Sentences": "\n".join(sentences)
                }

                updated_df = pd.concat([original_df, pd.DataFrame([new_row])], ignore_index=True)

                if len(updated_df) >= original_row_count + 1:
                    updated_df.to_excel(excel_file, index=False)
                    message = f"'{new_word}' added successfully!"
                else:
                    error = f"Failed to add '{new_word}'. Please try again."

        elif "remove_word" in request.form:
            word_to_remove = request.form.get("remove_word").strip().lower()

            if word_to_remove in original_df["Answer"].str.lower().values:
                updated_df = original_df[original_df["Answer"].str.lower() != word_to_remove]

                updated_df["No"] = range(1, len(updated_df) + 1)

                updated_df.to_excel(excel_file, index=False)

                message = f"'{word_to_remove}' removed successfully!"
            else:
                error = f"'{word_to_remove}' not found in the vocabulary list."

    updated_df = pd.read_excel(excel_file)

    return render_template(
        "add_vocabulary.html",
        message=message,
        error=error,
        df=updated_df[['No', 'Meaning','Answer']].to_html(classes="table table-striped", index=False),
    )



def split_into_lines(text):
    if isinstance(text, str):
        return text.replace("\n", "<br>").split("<br>")
    return [text]


if __name__ == "__main__":
    app.run(debug=True)
