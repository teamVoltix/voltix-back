# este archivo contiene funcionalidad para endpoint validacion y validate
1.enpoint of validation, recieve email of the user
2.check if this email exists already in user table
3. generate code, save it and send email to the client with this code
(Save a hashed version of the code with the email and an expiration timestamp in a temporary model.)


enpoint validate
4. recieve email and code 
5. check is code is belong to this email
6. check if code is not expired
(Validate Code:

    Ensure the code matches the hashed version stored.
    Check that the code hasn't expired.
    Confirm the code hasn't been used before.)
7. if it matching make it verified
if code is expired, ask to send request one more time 
if code was sent 2 times, ask to try again later


endpoint registration
8. recieve registration details
9. check if the email is verified, register with status is_active
10. delete email and code from email verification table (?)
(Optionally, remove the verification record to maintain a clean database.)

    Rate Limiting: Implement rate limiting to prevent abuse of the verification request endpoint.
    Code Expiration: Set a reasonable expiration time for verification codes (e.g., 10 minutes) to enhance security.
    Retry Limits: Limit the number of verification attempts to prevent brute-force attacks.
    User Feedback: Provide clear messages to users about the status of their verification and registration processes.
    Secure Code Storage: Always store verification codes in a hashed format to protect against data breaches.
    Email Content: Customize email templates to align with your brand and provide clear instructions.