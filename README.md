# pown-this-database
Simple REST interface to database with several vulnerabilities, project for Cheminformatics course

## What is this for?

This simple Bottle app provides a REST interface to a CSV database. It has several vulnerabilities allowing a user to falsify data or to corrupt the database. You can use it as an project for students to learn how data is processed and interpreted, or as a challenge prompting them to synthesize existing knowledge. Requires some understanding of HTTP verbs, how web APIs generally work, and a bit of Python.

## How to use it?

Someone (likely the instructor) should take the role of the administrator and deploy `db-manager.py`, creating a new database file. Students inspect the source code and attempt to attack the database through HTTP requests only. They can clone this repo and experiment with the code to understand how it works and design their attacks.

## Todo

- [ ] Deployment instructions
- [ ] Suggestions for exploring the code and writing tests
- [ ] Make and test Pip requirements
- [ ] Separate branch for didactic materials (like intermediate exercises
