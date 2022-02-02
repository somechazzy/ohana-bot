Introduction
---
Development of Ohana started back in August 2020 with the purpose of improving on existing bots' features and functionalities. Some bots that Ohana was inspired by are MAL, Dyno, Tatsu, Nadeko, Arcane and Hydra.

You can invite Ohana to see what it has to offer [using this link](http://invite.ohanabot.xyz).

Below is a guide on how to run Ohana locally, although you should keep a few things in mind:
* While this bot uses [disnake](https://github.com/DisnakeDev/disnake) (a discord.py fork), it does not utilize the commands framework built into the library. It uses however a custom commands handler that I wrote because I felt a bit limited by the framework. I can't promise you that it's better. The bot also does not use cogs or Task helpers.
* A lot of the code was written while I was still learning Python, therefore you'll find some poorly optimized code and generally not-the-best practices here and there. I re-wrote a portion of it, but it was too time-consuming so feel free to help!
* If you are familiar with Ohana, you'll notice that there are a few behavioural differences, as well as missing commands and features; this is mainly because I had to change and remove some code that could be exploited if your bot gets big enough.

Guide
===

In this guide we'll go over the steps necessary for you to get your bot up and running. I'll try to be as thorough as possible, but it is preferred if you had at least intermediate knowledge in Discord (permissions, role hierarchy, etc.), some experience with an IDE that supports Python, and some familiarity with Python.

### Step 1: Clone and Prepare to Run Locally

* Download and install [Python 3.8](https://www.python.org/downloads/release/python-3810/).
* If you don't already have an IDE or an editor, I recommend installing [PyCharm](https://www.youtube.com/watch?v=XsL8JDkH-ec).
* Clone this repository either using the [IDE's version control](https://www.youtube.com/watch?v=dziMbwRZrw8) or by just downloading the code as ZIP from above to manually extract and import it into the IDE.
* Once you've opened Ohana's code in your editor and finished setting up the interpreter and the venv, you'll need to install all the required libraries. This can be done quickly using the following command line. Paste it into the venv terminal:

    `pip install -r requirements.txt`
* Go to the file named `auth_template.py` in the main directory and read through it. I believe everything there is explained well enough except for the Firebase part, which is explained in step 3 below. Discord bot token is also explained in step 2.

### Step 2: Create a Discord Bot

* Go to [Discord Developer Portal](https://discord.com/developers/applications) and log-in if you haven't already
* Create a **New Application** and give it a name.
* Navigate to **Bot** tab on the left side of the screen and click **Add Bot**.
* Scroll down to **Privileged Gateway Intents** and enable **SERVER MEMBERS INTENT** and **MESSAGE CONTENT INTENT**.
* Scroll back up and **Click to Reveal Token**. The token you get must be kept secret, as it is equivalent to your bot's password. Anyone with this token can control your bot as if they own it.
* Take the token and paste it in the `auth_template.py` file inside the variable named `BOT_TOKEN`.

### Step 3: Create the Database

* Go to your [Firebase Console](https://console.firebase.google.com/) and create a new project
* Give it a name, maybe same as your bot's name.
* Once you're in, click **Build** on the top left side of the screen, then choose _Realtime Database_.
* Click **Create Database**, choose the location closest to you, and then keep it in Locked mode.
* After your database is created, click on **Rules** on the top bar and under "Edit rules" replace the existing text with the following and click publish:
    ```json
    {
      "rules": {
        "users": {
          "$uid": {
            ".write": "$uid === auth.uid",
            ".read": "$uid === auth.uid"
          }
        }
      }
    }
    ```
* Now we need information necessary for the bot to contact the database. To make our following steps clear, take the following piece of code and keep it in a notepad. We will be filling values for `databaseURL` and `serviceAccount`, while the rest will remain empty.
    ```python3
    FIREBASE_CONFIG = {
        "databaseURL": "",
        "serviceAccount": { 
  
        },
        "storageBucket": "",
        "apiKey": "",
        "authDomain": ""
    }
    ```
    1. First we will get `databaseURL` from the data tab, which can be found as in the screenshot below. Copy it and paste it inside the value for `databaseURL`.
       ![img.png](media/guide/fbdb_url.png)
    2. Next we need to get your `serviceAccount`. For this you will go to **Project Settings** (next to Project Overview on the top left), then to **Service accounts** tab, then you'll click **Generate new private key**. This will download a JSON file, open it with notepad and copy its content without the starting and ending curly brackets `{}`, and paste them inside under `serviceAccount` in the file we've been filling.
    3. Your file should now look similar to this:
        ```python3
        FIREBASE_CONFIG = {
            "databaseURL": "https://testproject-28508-default-rtdb.europe-west1.firebasedatabase.app/",
            "serviceAccount": { 
                "type": "service_account",
                "project_id": "testproject-28508",
                "private_key_id": "1e37386c0f81229758597632c63bc8d04bbec6aa",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIlMtFiqezCpvx7sdFRBAQDfvH0MdKQU2+iq\ngDrnVmNHNjRbFHyJ1p8SaZCGVU2PqQYMYCqj6tR2YJ\nyNm1mryZZjR3swQbtRD0cQ8ExgSpACiaX/iF/j0L6wftIEuJ2VEAtXFz0ewhOZuf\nUy1ABPFs2zgbCHpHdPRHOOGXdbHM+QwOjbbmtuUkOPs+dt+Y9fndyX\ngIIejsEZSafRvvH6pId\nKzhEXtPUS0s1VwaF5E6aLTJZQGE2oT2du+Asfj6ZAbdLhaw0pWBjdluH1WI9z/G4B/lN7JrjdgGD0sri65AXjFgA6WN32\nE19BTS4jAgMBAAECggEAHQ+zVn4tdKApP+xZZQSC72m1B0JJUSlL//rTzBI7TTrw\n2I3uyFU59TGOXUEKmH4j8xj+312/DRbsbseYr87M7J1VTK8DZkNF/oT+TxUW3zTW\nu/v3S2r+AaGibhyciQ0Uw8pOFq/fUSnGgf86QCtkWvkRv62dCFPhQYe\nQKGypDVPYtDs2t/r0LjV6s1PbJUHHrqCFzMT8jvpPmOGR\nEuYXS8j99Mw5Pso5452WpUPw1Kr8bH0XTlUMZE2jFcvpqnssXFvT0\neaMvllOA47eLZ4BNb/KXAENd5tugSG1uLayTE15ccQKBgQD0njXwkIirqVPBLjuB\nCdynMWomFQYTAU1h1dHlDZnmP+ktyqyidCiS6Av5cEop128EOw6JOxUH2RSHkMtb\nAJWSNZjTrxfaOtnIefxk9YWy654RNwQEekQnSyhD5HbIXnHjDdu9CAWeRQAAhj9K\n1f14c8x5sJoRmu7C5BXdkSNCh8j9ixe\nE2zMvgo46G0njl+F/qQ/i2Y1CgNHYUPddmngawrEB1cevQCDznH1WqGz/4QiE4Ok\n+B92sfChIMi6Ozs4Yb0eMbE4hO9upA6xEuILj1t6riwK9pAbXsMoA2rDpQ5FtkdI\nfji/dGVRLwKBgQDQovRMp2n6R+Toup8D8z5g19O6gWn54b13eaCZZZ1i9hXS+a9+\nq+ZDTmmQKccHovjMOfau81Z/qBZLfiMEDh6EYvRjcE6+0j0YMXslPQf4z9+0vSDP\nFN12SjMgnQb25R7r0tEdjG8GS8GxsM7g7F1RVCsNi6QM6gFE+cytarL3bQKBgQCZ\nPBy3/6bFDeTDDR5QQHPwiVvvmbIrjM4Y2l3Z\nr8cWXKhBCMaG7aAhBJBg1s8Db6aV\nyC/bNOS/cwEr45UH9Ipvw1yYYmZl4dxK\nIMkIfLk+fSSZRBw6CNKunST1X9PeHLgMjaNvtT0Pl2PH4\nE7pIaHYh8XmKv/iZNavcvihjgW2hNJ+\nssFT7eM430AvYzY9e9n8hjRs\n-----END PRIVATE KEY-----\n",
                "client_email": "firebase-adminsdk-130hl@testproject-28508.iam.gserviceaccount.com",
                "client_id": "112420256977677271110",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-780hl%40testproject-28508.iam.gserviceaccount.com"
            },
            "storageBucket": "",
            "apiKey": "",
            "authDomain": ""
        }
        ```
    4. Everything in this file is now the value to `FIREBASE_CONFIG` variable in the `auth_template.py` file, so copy and paste it there.
    
### Step 4: Run locally

* After you've filled all the variables in `auth_template.py`, rename the file to `auth.py`.
* Go to `settings.py` file and read through it. Make all the changes that you deem necessary.
* Everything is now ready. Run `ohana.py` and give your bot a try!
 
