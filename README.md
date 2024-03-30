# google-contacts-fix

Change prefix of all phone numbers from `8` to `+370`.

## Requirements

* Python 3.8
* A project on Google Developer

## Google setup

* Create a new project. Grant access to the Google account which you want modified.
* Create app credentials: 
  * _APIs & Services_
  * _Credentials_ 
  * _Create Credentials_ 
  * _Oauth Client ID_ 
  * _Desktop App_
  * Download client secret JSON, save as `credentials.json` in the project folder.
* Set up required scopes: 
  * _APIs & Services_ 
  * _Oauth consent screen_, enter mandatory, _Save and continue_ 
  * _Add or remove scopes_, pick `.../auth/contacts`, _Save and continue_ 
  * _Add users_, add your email, _Save and continue_

If everything is set up properly, you'll be redirected to pick an account when running. Check if contacts can be listed.

## Usage

```python main.py --help```