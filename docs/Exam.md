# Exam Docker
The exam website is located in the subdirectory `/exam`.

The default proctor username is `proctor` and the password is
specified in an environment variable in `/docker-compose.yml`.

Each exam is 20 questions long, and students have 1 hour to
complete it.

Exam-related data is stored in the `/examdata` directory:
 - `questions.csv` - A CSV file containing the question bank for the exam.
 - `examstorage.enc` - The encrypted database information.
 
**Limitation:** The exam database is limited to a size of a little under 256 MiB.
 
## Environment Variables:
 - `DEFAULT_PROCTOR_PASSWORD` - The initial password for the proctor interface
   login. Please change this password before deploying
 - `FILE_ENCRYPTION_SECRET` - The secret for the encrypted files. You should change
   this to a long, unique password before first deployment. It is unlikely that 
   this password will need to be manually typed over the lifetime of this app.
   Do not change this value after deploying the app, otherwise data loss may 
   occur. (Not implemented yet)