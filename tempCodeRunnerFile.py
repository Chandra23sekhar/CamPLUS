if session:
    #     #print(session.get('user')['userinfo']['name'])
    #     t = user_balance.query.filter_by(user_name=session.get('user')['userinfo']['name']).first()
    #     return render_template("home.html", session=session.get('user'), name=session.get('user')['userinfo']['name'],
    #         e=session.get('user')['userinfo']['email'],
    #         b=np.round(t.balance, 3), indent=4)
    # else: