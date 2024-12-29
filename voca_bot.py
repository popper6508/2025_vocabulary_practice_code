import pandas as pd
import random
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def vocabulary():
    excel_file = "vocabulary.xlsx"
    df = pd.read_excel(excel_file)

    vocabulary_data = df.to_dict(orient="records")

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
            meaning = row_data["Meaning"]
            sentence = row_data["Sentences"].replace(correct_answer, "_____")

        elif "check_answer" in request.form:
            if "word" in request.form:
                user_input = request.form.get("word").strip().lower()
                selected_row = int(request.form.get("selected_row"))
                row_data = df.iloc[selected_row]
                correct_answer = row_data["Answer"]
                meaning = row_data["Meaning"]
                sentence = row_data["Sentences"].replace(correct_answer, "_____")
                feedback = "Correct!" if user_input == correct_answer.lower() else "Try again!"

        elif "show_answer" in request.form:
            selected_row = int(request.form.get("selected_row"))
            row_data = df.iloc[selected_row]
            correct_answer = row_data["Answer"]
            meaning = row_data["Meaning"]
            sentence = row_data["Sentences"].replace(correct_answer, "_____")
            show_answer = correct_answer

    return render_template(
        "visual.html",
        meaning_lines=split_into_lines(meaning),
        sentence_lines=split_into_lines(sentence),
        correct_answer=correct_answer,
        feedback=feedback,
        user_input=user_input,
        show_answer=show_answer,
        data=vocabulary_data,
        start=start,
        end=end,
        selected_row=selected_row,
        df=df.to_html(classes="table table-striped", index=False),
    )


def split_into_lines(text):
    """
    Generalized function to split text into multiple lines.
    Handles \n, ;, ., or other delimiters.
    """
    if isinstance(text, str):
        return text.replace("\n", "<br>").split("<br>")
    return [text] 


if __name__ == "__main__":
    app.run(debug=True)
