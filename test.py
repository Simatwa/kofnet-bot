import re

pattern = r"(\n)(?=\s*$)"

text = """
<b>NEW SNI TEST NET</b>
www.who.int [unlimited net unknown]
ligibet.co.ke
104.18.8.127
safaricom.zerod.live
coregateway.app.dlight.com
www.betika.com
shoponbloom.com

<b>Airtel</b>

104.18.8.127 [v2ray]
portal.ncnd.vodacom.co.tz [Also use it as a realm host on HA tunnel]
africanstorybook.org
www.edraak.org/en/
www.khanacademy.org/
www.edx.org/
moodle.com/
www.nafham.com/
www.learningequality.org/kolibri
www.syafunda.co.zm/
digital-campus.org/oppiamobile
www.leaphealthmobile.com/
www.classera.com/en/home/
m-shule.com
internetofgoodthings.org

<b>Safaricom</b>
104.21.51.108 [V2RAY]
www.mwalimoo.com./m/start
https://elearning.longhornpublishers.com/login/index.php
https://ke.goodinternet.org
"""

out = re.sub(pattern, "<br>", text)

print(out)
