[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zUKWOP3z)
CMPUT404-project-socialdistribution
===================================

CMPUT404-project-socialdistribution

See [the web page](https://uofa-cmput404.github.io/general/project.html) for a description of the project.

Make a distributed social network!

## License

MIT License

## Copyright

The authors claiming copyright, if they wish to be known, can list their names here...

* 

## Names of Teammates:
* Bennet Steem
* Ethan Keys
* Julia Dantas
* Shaan Adatia
* Casper Nguyen
* Theresa Gabrielle Tian

## Heroku Details
* Dashboard link: https://dashboard.heroku.com/apps/f24-project-chartreuse

## Tests
To run the tests, run the following command in the root directory of the project:
```
python manage.py test chartreuse
```

## Citations

### Stack Overflow Citations

#### Citation 1
From https://stackoverflow.com/questions/150505/how-to-get-get-request-values-in-django by camflan, Downloaded on 2024-09-28
This citation helped us understand how to get queries from a GET request in Django. This was used in chartreuse/api_handling/users.py to get the query parameters from the GET request on lines _ to _.

#### Citation 2
From https://stackoverflow.com/questions/25963552/json-response-list-with-django by Majid Zandi, Downloaded on 2024-09-28
This citation helped us understand how to return a JSON response in Django for lists of objects.  This was used in chartreuse/api_handling/users.py to return a JSON response of a list of users on lines _ to _.

#### Citation 3
From https://stackoverflow.com/questions/4994789/django-where-are-the-params-stored-on-a-put-delete-request by Ni Xiaoni, Downloaded on 2024-09-28
This citation helped us understand how to get the parameters from a PUT request in Django. This was used in chartreuse/api_handling/users.py to get the parameters from the PUT request on lines _ to _.

#### Citation 4
From https://stackoverflow.com/questions/68595593/how-to-base64-encode-an-image-from-url-rather-than-file, Downloaded on 2024-09-30
This citation helped us understand how to base64 encode an image from a URL in Python. This was used in chartreuse/api_handling/images.py to base64 encode an image from a URL on lines _ to _.

### Django Documentation Citations

#### Citation 1
This https://docs.djangoproject.com/en/5.1/topics/pagination/ helped us to understand how to paginate objects in Django. This was used in chartreuse/api_handling/users.py to paginate the users on lines _ to _.

#### Citation 2
* https://docs.djangoproject.com/en/5.1/topics/testing/overview/
* https://docs.djangoproject.com/en/5.1/topics/testing/tools/#overview-and-a-quick-example
<br>
These sources helped us to understand how to write tests in Django. This was used in chartreuse/tests.py to write tests for the User model on lines _ to _.

#### Citation 3
This https://docs.djangoproject.com/en/3.2/_modules/django/contrib/auth/password_validation/ helped us to understand how to validate passwords in Django. This was used in chartreuse/api_handling/users.py to validate passwords on lines _ to _.

#### Citation 4
This https://docs.djangoproject.com/en/5.1/ref/models/fields/#choices helped us to understand how to use choices in Django models. This was used in chartreuse/models.py to use choices in the User model on lines _ to _.

### AI / LLM Citations

#### Citation 1
Generated a response uing OpenAI, ChatGPT using the prompt "How to set up Django auth?"
The response was used in chartreuse/api_handling/users.py to help set up Django auth on lines _ to _.

#### Citation 2
Generated a response using OpenAI, ChatGPT using the prompt "How to validate passwords in Django?"
The response was used in chartreuse/api_handling/users.py to help validate passwords in Django on lines _ to _.

### Other Citations

#### Citation 1
This https://www.w3schools.com/python/python_json.asp helped with figuring out how to put a string into a JSON object. 
This was used in chartreuse/api_handling/users.py to convert a string into a JSON object on lines _ to _.

#### Citation 2
This https://www.geeksforgeeks.org/user-authentication-system-using-django/ helped with understanding how to set up user authentication in Django.

#### Citation 3
This https://www.geeksforgeeks.org/how-to-open-an-image-from-the-url-in-pil/ helped with understanding how to open an image from a URL in PIL. This was used in chartreuse/api_handling/users.py to open an image from a URL on lines _ to _.

#### Citation 4
<<<<<<< HEAD
This https://getbootstrap.com/docs/5.3/getting-started/introduction/ helped step up bootstrap for the project. This was used in chartreuse/templates/base.html and the resulting CSS and HTML files that will be made for the site

#### Citation 4
This https://getbootstrap.com/docs/5.3/getting-started/introduction/ helped step up bootstrap for the project. This was used in chartreuse/templates/base.html and the resulting CSS and HTML files that will be made for the site

#### Citation 5
This https://docs.github.com/en/rest/activity?apiVersion=2022-11-28 helped with understanding how to use the GitHub API. This was used in chartreuse/api_handling/github.py to use the GitHub API on lines _ to _.
=======
This https://getbootstrap.com/docs/5.3/getting-started/introduction/ helped step up bootstrap for the project. This was used in chartreuse/templates/base.html and the resulting CSS and HTML files that will be made for the site
>>>>>>> 8714397 (Created templates folder and base.html,)
