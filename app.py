from flask import Flask, render_template, request, redirect, url_for, session, flash
from random import randint
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Load login credentials from CSV
login_data = pd.read_csv('logins.csv')
print(login_data.columns)  # Check column names for debugging

login_data = login_data.set_index('Username').T.to_dict('list')


# Temporary in-memory storage
users = {}  # Store Aadhaar and OTP
votes = []  # Store hashed Aadhaar and their vote
voters = {}  # Dictionary to store Aadhaar numbers that have voted

# Email credentials
SENDER_EMAIL = "shreeyamo123@gmail.com"  # Replace with your email
SENDER_PASSWORD = "djog arjk vuur onyl"  # Replace with your email password or app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


# Function to send OTP via email
def send_otp_via_email(otp, recipient_email):
    subject = "Your OTP for Voting"
    body = f"Your OTP for voting is: {otp}"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the server and login
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Send email
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()  # Close the connection

        # Flash message to indicate successful OTP sending
        flash("OTP sent successfully to your registered email address.", "success")
    except Exception as e:
        # Flash message to indicate error in sending OTP
        flash(f"Failed to send OTP email. Error: {e}", "error")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']

        # Verify user credentials
        if username in login_data and login_data[username][0] == password:
            session['Username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('cast_vote'))
        else:
            flash("Invalid username or password. Please try again.", "error")
    return render_template('login.html')


@app.route('/cast_vote', methods=['GET', 'POST'])
def cast_vote():
    if request.method == 'POST':
        aadhar = request.form['aadhar']
        otp = randint(100000, 999999)  # Generate random 6-digit OTP
        users[aadhar] = otp  # Store OTP in memory
        session['aadhar'] = aadhar  # Save Aadhaar to session

        # Check if Aadhaar matches specified number
        if aadhar == "123456789012":
            send_otp_via_email(otp, "shreeyamo123@gmail.com")  # Send OTP to your email
        else:
            flash("Aadhaar not recognized for automatic OTP sending.", "error")

        return render_template('otp.html')  # Go to OTP entry page
    return render_template('register.html')


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    otp = request.form['otp']
    aadhar = session.get('aadhar')
    if aadhar and users.get(aadhar) == int(otp):
        # Check if the Aadhaar has already voted
        if voters.get(aadhar):
            flash("You have already voted. Multiple votes are not allowed.", "error")
            return redirect(url_for('vote_confirmation'))
        return render_template('vote.html')  # Go to voting page
    else:
        flash("Wrong OTP entered. Please try again.", "error")
        return redirect(url_for('cast_vote'))


@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    selected_party = request.form.get('party')
    aadhar = session.get('aadhar')
    if aadhar and selected_party:  # Ensure Aadhaar and party are selected
        # Check if the Aadhaar has already voted
        if voters.get(aadhar):
            flash("You have already voted. Multiple votes are not allowed.", "error")
            return redirect(url_for('vote_confirmation'))

        # If not voted, proceed to cast the vote
        hashed_aadhar = hashlib.sha256(aadhar.encode()).hexdigest()
        votes.append({"aadhar": hashed_aadhar, "vote": selected_party})  # Store vote with hashed Aadhaar
        voters[aadhar] = True  # Mark this Aadhaar as having voted
        flash("Vote cast successfully!", "success")
        return redirect(url_for('vote_confirmation'))  # Go to confirmation page
    else:
        flash("Please select a party.", "error")
        return redirect(url_for('cast_vote'))


@app.route('/vote_confirmation')
def vote_confirmation():
    return render_template('vote_confirmation.html')


@app.route('/view_votes')
def view_votes():
    return render_template('view_votes.html', votes=votes)



if __name__ == "__main__":
    app.run(debug=True)
