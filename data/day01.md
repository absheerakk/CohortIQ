## **Python Learning Path: Basics to API Requests**

## **1. Python Fundamentals**

* Variables \& data types (strings, integers, floats, booleans)
* Type conversion \& basic input/output
* Arithmetic \& comparison operators

## **2. Control Flow**

* if / elif / else statements
* for and while loops
* break , continue , pass

## **3. Data Structures**

* Lists, tuples, sets
* Dictionaries (key-value pairs)
* List comprehensions

## **4. Functions**

* Defining and calling functions
* Parameters, arguments, default values
* Return values \& scope
* \*args and \*\*kwargs

## **5. String Manipulation**

* Slicing \& formatting (f-strings)
* Common string methods ( .split , .join , .strip , etc.)

## **6. File Handling**

* Reading \& writing files
* Using with open(...) context managers

## **7. Error Handling**

* try / except / finally
* Raising exceptions
* Common built-in exceptions

## **8. Modules \& Packages**

* Importing standard library modules ( os , math , random , datetime )
* Installing packages with pip

## **9. Object-Oriented Basics** ***(optional but useful)***

* Classes \& objects
* **init** , methods, attributes

## **10. Working with JSON**

* Parsing JSON with the json module
* Serializing Python dicts to JSON

## **11. Making API Requests**

* Install \& import requests
* GET requests \& reading responses
* Query parameters \& headers
* POST requests with a JSON body
* Handling status codes \& errors
* Parsing the JSON response

## **Research**

What is API

What is HTTP

HTTP Methods

HTTP Headers


**Python API Exercises**

## **Exercise 1 — Fetch a Random Joke**

* **API:** https://official-joke-api.appspot.com/random\_joke
* **Task:** Make a GET request and print the setup and punchline of the joke.
* **Bonus:** Loop it 5 times to get 5 different jokes.

## **Exercise 2 — Get Current Weather**

* **API:** OpenWeatherMap (free tier) — openweathermap.org
* **Task:** Sign up for a free API key, then fetch the current weather for your city. Print the temperature, humidity, and description.
* **Bonus:** Convert the temperature from Kelvin to Celsius.

## **Exercise 3 — Fetch a Random Dog Image**

* **API:** https://dog.ceo/api/breeds/image/random
* **Task:** Make a GET request and extract the image URL from the response. Print it.
* **Bonus:** Ask the user to input a breed name and fetch an image for that specific breed.

# Bonus hint

breed = input("Enter a breed: ").lower()

url = f"https://dog.ceo/api/breed/{breed}/images/random"

## **Exercise 4 — Search for Books**

* **API:** https://openlibrary.org/search.json?q=your+book+name
* **Task:** Ask the user to input a book title, send it as a query parameter, and print the top 5 results with title and author.
* **Bonus:** Handle the case where no results are found gracefully.

query = input("Enter a book title: ") url = "https://openlibrary.org/search.json"

params = {"q": query}

## **Exercise 5 — Get a GitHub User's Info**

* **API:** https://api.github.com/users/{username}
* **Task:** Ask the user to input a GitHub username and display their name, bio, public repos count, and followers.
* **Bonus:** List their 5 most recent public repositories using

https://api.github.com/users/{username}/repos .

username = input("Enter a GitHub username: ") url = f"https://api.github.com/users/{username}"

## **Exercise 6 — POST Request Practice**

* **API:** https://jsonplaceholder.typicode.com/posts
* **Task:** Send a POST request with a JSON body containing a title , body , and userId . Print the response.
* **Note:** This is a fake/mock API — great for safely practicing POST requests without any side effects.



