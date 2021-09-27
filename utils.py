import requests
from flask import current_app

def requests_data(url, timeout=5, params=None, headers=None, data=None,  auth=None, method='post'):
    if method == 'post': 
        req_func = requests.post
    else:
        req_func = requests.get
    try: 
        responce = req_func(url, params=params, headers=headers, data=data,  auth=auth, 
                            timeout=timeout)
        result = responce.json()
        responce.raise_for_status()
    except ValueError as errv:
        current_app.logger.exception("Exc ValueError!")
        return {"error": "value error!", "error_message": str(errv)}, 500
    except requests.exceptions.HTTPError as errh:
        current_app.logger.error(result)
        current_app.logger.exception("Exc HTTPError!")
        return {"error": "Http Error!", "error_message": str(errh)}, responce.status_code
    except requests.exceptions.ConnectionError as errc:
        current_app.logger.exception("Exc ConnectionError!")
        return {"error": "Error Connecting:!", "error_message": str(errc)}, 404
    except requests.exceptions.RequestException as err:
        current_app.logger.exception("Other requests.exception!")
        return {"error": "OOps: Something Else!", "error_message": str(err)}, responce.status_code
    return result, 200
