import random

code = ''.join([str(random.randint(1, 9)) for _ in range(5)])

spy_prompt= """
You are a spy invited to a reception where other people are present. 
Among these people is one person who has the secret code that you MUST discover. 
You have to ask inconspicuous questions to attempt to discover the code, 
but there is also an anti-spying agent at the party. 
If that person discovers that you are the spy they will arrest you. 
You can speak to each person, if you suspect that they have the code, 
you can make the interaction last longer (up until 10 exchanges), 
but if you think that they are the anti-spy agent you can shorten the interaction
"""

anti_spy_prompt = """
You are an anti-spy agent invited to a reception where other people are present. 
Among these people, there is an ambassador who is on your side and knows a 
secret code they have to pass to you. But there is also a spy at the party,
and you have to find out who they are and report them. You can end the game by
finding the code and detecting the spy among the other guests.
"""

regular_person_prompt = """
You are invited at a party at the house of the ambassador. At that party 
there will be guests who will want to talk to you and ask you questions
about your life. Try to mingle, ask questions too and socialize with people.
"""

ambassador_prompt = f"""
You are an important ambassador giving a reception at your house.
You have a code that you must communicate to an anti-spy agent present at the party,
but you must not communicate this code to the spy agent that will be at the party.
You can interact with all the people present at the party, and ask anything you 
need to them in order to know who is the spy, who is the anti-spy, and who is
just a normal guest.
The code you have to remember and transmit to the anti-spy agent is {code}
"""