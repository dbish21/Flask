from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

# Using a constant for the session key ensures consistency throughout the app
# and makes it easier to change the key name if needed in the future
RESPONSES_KEY = "responses"

app = Flask(__name__)
# Secret key is necessary for Flask to use sessions and flash messages
app.config['SECRET_KEY'] = "donthave1"
# Disable intercept redirects to avoid issues with the debug toolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.route("/")
def show_survey_start():
    """Select a survey."""
    # Render the start page, passing the survey object to display its title and instructions
    return render_template("survey_start.html", survey=survey)

@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses."""
    # Initialize an empty list in the session to store responses
    # This ensures a fresh start for each survey attempt
    session[RESPONSES_KEY] = []
    return redirect("/questions/0")

@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""
    # Retrieve the user's answer from the form data
    choice = request.form['answer']

    # Append the new response to the existing list in the session
    # This allows us to keep track of all answers without using a database
    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    if (len(responses) == len(survey.questions)):
        # If all questions are answered, redirect to the completion page
        return redirect("/complete")
    else:
        # Otherwise, redirect to the next question
        # Using len(responses) ensures we go to the correct next question
        return redirect(f"/questions/{len(responses)}")

@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""
    responses = session.get(RESPONSES_KEY)

    if (responses is None):
        # If there are no responses, the user hasn't started the survey properly
        # Redirect to the start to ensure the session is set up correctly
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        # If all questions are answered, always redirect to the thank you page
        # This prevents accessing questions after survey completion
        return redirect("/complete")

    if (len(responses) != qid):
        # This check ensures that questions are answered in order
        # It prevents skipping questions or going back to previous ones
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    # If all checks pass, display the current question
    question = survey.questions[qid]
    return render_template(
        "question.html", question_num=qid, question=question)

@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""
    # Simple route to display the completion page
    return render_template("completion.html")
