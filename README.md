# SLOT - Supervised Learning Opportunities by Text

## Project Status
**WE'RE IN ALPHA**
A short phase in which you prototype solutions for your users' needs. Test with a small group of users or stakeholders, and getting early feedback about the design of the product.

## What is SLOT?
Medical students need hands-on experience of carrying out procedures in hospitals, under supervision. For instance, they need to learn how to carry out venepuncture or catheterisation. Opportunities for them to learn occur unpredictably, and currently lots of those opportunities aren’t taken, as there might not be a medical student in the vicinity at the point where a junior doctor is available to train them.  

We have built a way for junior doctors to notify medical students that the opportunities are available, and for medical students to take the opportunities. Junior doctors use a web application to add opportunities. Medical students are notified about these opportunities by text message, and can respond by replying with a code. Opportunities are assigned on a first come, first served basis, and the first student to respond is notified by text message. Unsuccessful respondents are notified that the opportunity has been taken. Junior doctors can then record whether the student attended the opportunity or not. 

We plan to use what we’ve built to research whether this is an appropriate way of meeting this latent need. We plan to trial this first in one hospital, and to gather data on whether this increases the quality of training of medical students, particularly whether it enables students to practice - under supervision - these essential medical skills more frequently. 

## Design Principles

#### Build for browser compatibility
Some users will need to access the app on outdated browsers so where possible we should avoid use of anything but the most basic javascript.

#### Mobile device compatibility
Fairly easily solved by the use of SMS messages - supported by all current models of mobile phone! :)
We may need to expand to other methods of communicating with users at a later point, but we will use solely SMS whilst in Alpha.

## Current Technology Stack
#### Application
+ Python + Flask / Jinja2 (Language + Web Server Framework)
+ Bootstrap CSS
+ Redis for caching

#### Database
+ Fieldbook.com

#### Hosting
+ Heroku

#### Third-party Services
+ Twilio (SMS Messaging)


