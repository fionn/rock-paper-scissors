# rockpaperscissors

REQUIREMENTS
============

The file 'consumer.txt' must contain two lines, containing the consumer secret and key respectively.

Similarly, 'access.txt' must contain two lines, containing the access token and key.

A 'reponses.txt' file should also be populated with strings that python can format. 
Valid labels are "Win","win","Draw","draw","Lose","lose" and "percentage".
Title case labels give title case examples, e.g. Rock, Paper, Scissors, similarly for lower case labels.
The percentage label returns a number between 0 and 100.

For example:
```python
	I win, with {win}. ## I win, with rock.
	{Lose} will always lose. ## Paper will always lose.
	There is a {percentage}% chance of me choosing {draw}. ## There is a 13% chance of me choosing scissors.
```
