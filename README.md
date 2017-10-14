# luckyoneshot
Web tier for the Lucky One Shot automated batch checker for Taiwan's Uniform Invoice lottery (Python/Pyramid).

Checks an image of several receipts in one shot, and informs user if any are winning.
Only works for receipts with QR codes, nearly all shop receipts have these, whereas restaurant receipts typically do not.
Displays a feedback image to the user with the receipts which it managed to read circled in green.

## Build instructions

* Install libzbar
* Build luckyoneshot_cpp
* Clone/checkout this repo
* Modify recaptcha site key in views.py:homepageView() (or disable the captcha if not needed)
* In your checkout directory:
```
export RECAPTCHA_SECRET="<your recaptcha secret>"; export IMAGE_DIR="/tmp"; 
export IS_DEV_BOX=”true”;
export CPP_EXE="/path/to/luckyoneshot_cpp"; pserve development.ini
```
* You should see e.g.

```
Python: IS_DEV_BOX=False
Starting server in PID 5386.
Serving on http://0.0.0.0:6543
```

* Point your browser to http://127.0.0.1:6543 and be lucky!

## Use instructions
* Click the snapshot button
  * On a mobile phone browser this should directly open the camera. Snap a photo of several receipts.
  * On a PC browser, select an image of several receipts
* Click the submit button and upload the image
* Complete the captcha if required
* Wait a few seconds while Lucky One Shot checks the receipts.

