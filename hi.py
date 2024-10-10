import smtplib

# Replace with your email and app password
email = "eshwanthkartitr@gmail.com"
app_password = "jyxt iwfk aubt qdrg"  # Use an App Password if using Gmail

try:
    # Set up the server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Log in to the server
    server.login(email, app_password)

    # Send the email
    from_email = email
    to_email = "eshwanthkartitr@gmail.com"
    message = "Subject: Test Email\n\nThis is a test email sent from Python."
    server.sendmail(from_email, to_email, message)

    print("Email sent successfully!")

except Exception as e:
    print(f"Failed to send email. Error: {e}")

finally:
    # Quit the server
    server.quit()