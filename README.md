# luckyoneshot
Web tier for the Lucky One Shot automated batch checker for Taiwan's Uniform Invoice lottery (Python/Pyramid).

## Build instructions

* Install libzbar
* Build luckyoneshot_cpp
* Clone/checkout this repo
* Modify recaptcha site key in views.py:homepageView()
* In your checkout dir: `export RECAPTCHA_SECRET="<your recaptcha secret>"; export IMAGE_DIR="/tmp"; 
export IS_DEV_BOX=”true”;
export CPP_EXE="/path/to/luckyoneshot_cpp"; pserve development.ini`
* Point your browser to http://127.0.0.1:6543 and be lucky!


