import flask as f
def render(html: str, **kwargs):
    
    uid = f.g.user.get('uid', -1) if hasattr(f.g, 'user') else -1
        
    return f.render_template(html, uid=uid, **kwargs)
