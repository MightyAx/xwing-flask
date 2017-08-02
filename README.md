# xwing-flask
X-Wing Tournament Manager, built in Flask using Redis for data storage.

Currently this application is pre-alpha and in active development.
The best software for running x-wing tournaments is Java only: https://github.com/Killerardvark/CryodexSource. Online swiss tournament managers such as http://challonge.com/ do not cater for the specific matching requirements set by the publishers FFG.

The goal of this project is to create an online application that uses the FFG matching ruleset without the need for a full laptop.

The initial release is planned to be barebones, one administrator per tournament.

You can track progress on the Project tab and submit feature requests on the Issues tab.

Hosting is provided by heroku which means:
- Any feature branch that submits a pull request will have a review app created.
- A staging environment is created from the master branch here: https://xwing-flask-master.herokuapp.com
- A production environment will be created once staging has passed cert here: https://xwing.herokuapp.com
- I'd like to setup TDD but not sure I can get thaat to autorun on heroku without paying for it yet.

Future functionality on the wishlist:
- Have players log their own matches
- Scoreboard view
- Table view
- Where is a player supposed to be
- Round Timings
- Round Notifications
- Army import from xwing-builder
- Live Score tracking
- iOS / GooglePlay app (for notifications)

Any comments?
Let me know on twitter: twitter.com/Mighty_Ax
