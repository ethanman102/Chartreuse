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
* Service address: https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/
* Port:
* Hostname:
* Prefix:
* Username for HTTP Basic Auth:
* Password for HTTP Basic Auth:

## Tests
To run the tests, run the following command in the root directory of the project:
```
python manage.py test chartreuse
```

## API Documentation
To view the API documentation, go to the following link after running the server locally: http://127.0.0.1:8000/chartreuse/schema/swagger-ui/

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

### Citation 5
From https://stackoverflow.com/questions/23154525/django-generic-detail-view-must-be-called-with-either-an-object-pk-or-a-slug#:~:text=But%20as%20addition,%20issue%20Generic%20detail by Alex downloaded 2024-10-02
This citation helped us to understand the generic detail view being unable to retrieve a user due to a lack of pk specified directly in the Model class. Alex's response helped us to understand to override get_object()
From the detail view. Used on lines _ to _.

We furthermore used:
* https://medium.com/@katheller/how-to-use-get-object-in-drf-generics-views-examples-a7b879ff2d50#:~:text=In%20Django%20REST%20Framework%2C%20if%20you%20override%20the,expected%20because%20any%20permission%20was%20taken%20into%20consideration. (Author Katarzyna Antonik-Heller May 19,2023) To learn how to override get_object

### Citation 6
From https://stackoverflow.com/questions/9932047/html-multiple-name-value-for-an-element Author: Madara's Ghost on March 29, 2012
This citation helped us to understand how to data inside a form without having to have it inputted into a tetx box. The main issue with needing this approach was found in profile/html where we needed to send the requester and requestee user id's in the request body to be processed for usage. This technique was used in lines _ to _.



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

#### Citation 3
Generated a response using OpenAI, ChatGPT using the prompt "How to use swagger api documentation in Django?" and "How to create documentation using swagger to add additional information to the API, like a description, response, parameters, etc?" These responses were used in chartreuse/urls.py and chartreuse_admin/settings.py and chartreuse_admin/urls.py to set up the swagger routes on lines _ to _.
We also used these generated responses in chartreuse/api_handling/users.py to add additional information to the API on lines _ to _.

#### Citation 4
Generated a response using OpenAI, ChatGPT using the prompt "How to use the filter method to find users who exist in both the followers and following lists". The response was used in chartreuse/api_handling/friends.py to find the mutual followers/friends of a particular author.

We additionally used the following resources:
* https://www.rootstrap.com/blog/automating-django-rest-apis-documentation-made-easy-with-drf-spectacular-part-2
* https://drf-spectacular.readthedocs.io/en/latest/
* https://rohitkrgupta.medium.com/swagger-with-django-made-easy-a-drf-spectacular-explainer-20b18bb4c33c

### Citation 5
https://docs.djangoproject.com/en/5.1/ref/templates/builtins/ Accessed: October 6 2024
Learned how to input a URL tag to use in a form. We initially ran into the issue of form's not working due to the requests loop. This allows us to use the same URL in the loop over and over again. Used in lines _ to _ of profile.html.

### Other Citations

#### Citation 1
This https://www.w3schools.com/python/python_json.asp helped with figuring out how to put a string into a JSON object. 
This was used in chartreuse/api_handling/users.py to convert a string into a JSON object on lines _ to _.

#### Citation 2
This https://www.geeksforgeeks.org/user-authentication-system-using-django/ helped with understanding how to set up user authentication in Django.

#### Citation 3
This https://www.geeksforgeeks.org/how-to-open-an-image-from-the-url-in-pil/ helped with understanding how to open an image from a URL in PIL. This was used in chartreuse/api_handling/users.py to open an image from a URL on lines _ to _.

#### Citation 4
This https://getbootstrap.com/docs/5.3/getting-started/introduction/ helped step up bootstrap for the project. This was used in chartreuse/templates/base.html and the resulting CSS and HTML files that will be made for the site

#### Citation 5

This https://getbootstrap.com/docs/5.3/getting-started/introduction/ helped step up bootstrap for the project. This was used in chartreuse/templates/base.html and the resulting CSS and HTML files that will be made for the site

#### Citation 6
This https://docs.github.com/en/rest/activity?apiVersion=2022-11-28 helped with understanding how to use the GitHub API. This was used in chartreuse/api_handling/github.py to use the GitHub API on lines _ to _.

### Citation 7
Used Bootstrap Documentation https://getbootstrap.com/docs/5.0/components/navs-tabs/ for tabs and nav bars to construct a tab navaigation bar in chartreuse/templates/profile.html using one of their examples on lines _ to _.  

### Citation 8
Used this YouTube Video https://www.youtube.com/watch?v=dXkmPAnqnTE (Posted August 27, 2020) to learn how to use different generic views (specifically Detail View) and learn the theory of thing's it overrides. Used on lines _ to _ on chartreuse/views.py.

Used https://www.linkedin.com/pulse/creating-api-documentation-django-swagger-atomixweb-15twf/ and
https://www.515tech.com/post/swagger-for-django-creating-useable-api-documentation to understand how to create API documentation in Django. This was used in chartreuse/urls.py and chartreuse_admin/settings.py and chartreuse_admin/urls.py to create API documentation on lines _ to _.

### Citation 9
Used https://www.django-rest-framework.org/api-guide/viewsets/#example_3 to understand how to use viewsets in Django. This was used in chartreuse/api_handling/users.py and chartreuse/api_handling/likes.py to use viewsets on lines _ to _.

### Citation 10
Used https://www.linkedin.com/pulse/creating-api-documentation-django-swagger-atomixweb-15twf/ to understand how to create API documentation in Django. This was used in chartreuse/api_handling/users.py and chartreuse/api_handling/likes.py to create API documentation on lines _ to _.

### Citation 11
Used https://www.youtube.com/watch?v=hA_VxnxCHbo&t=570s Youtube video by the user: The Dumbfolds (Accessed October 7, 2024) For helping how to write Django views tests and testing their logic. This idea was used in test_project_views.py for the whole document.

