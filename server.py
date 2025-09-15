from flask import Flask, render_template, request, redirect, make_response, url_for
if request.cookies.get(AGE_COOKIE) == "1":
# Default country: detect from param or use "ALL"
country = request.args.get('country', 'ALL')
theme = request.cookies.get('theme', 'dark')
return render_template('index.html', sites=SITES.keys(), country=country, theme=theme)
return render_template('age_gate.html')


@app.route('/confirm_age', methods=['POST'])
def confirm_age():
resp = make_response(redirect(url_for('home')))
resp.set_cookie(AGE_COOKIE, "1", max_age=60*60*24*30)
return resp


@app.route('/set_theme', methods=['POST'])
def set_theme():
theme = request.form.get('theme', 'dark')
resp = make_response(redirect(url_for('home')))
resp.set_cookie('theme', theme, max_age=60*60*24*365)
return resp


@app.route('/search', methods=['GET', 'POST'])
def search():
q = request.values.get('q', '').strip()
if not q:
return redirect(url_for('home'))


selected = request.values.getlist('site')
if not selected:
selected = list(SITES.keys())


country = request.values.get('country', 'ALL')
encoded = urllib.parse.quote_plus(q)
results = []
for name in selected:
pattern = SITES.get(name)
if not pattern:
continue
url = pattern.replace('{q}', encoded)
# If pattern supports country placeholder, replace it (optional)
url = url.replace('{cc}', country)
results.append({'site': name, 'url': url})


return render_template('results.html', query=q, results=results, country=country)


if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
