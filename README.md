# Fidbot
Twitch chatbot for twitch.tv/fideliasfk

Fid's Broken Boner bot!

The aim of the game is to bet how many minutes it will take before FideliasFK either breaks his legs or dies in Arma 3.
The one with the closest time wins the title "Broken Boner"!

Commands below might not be completely up to date. Use !bonercommands to recieve the latest commands.

----------------------------------------
How it works:
To allow people to start betting enter !openbets. After bets are opened, enter !bet plus the number of minutes to enter the pool. 
When the mission starts use !starttimer. The bets will be closed and a timer will be started.
When Fid dies or breaks his legs enter !stoptimer. The timer will be stopped and a winner will be anounced.

The winner is the one with the closest bet, with a maximum of 5 minutes. If Fid does not break a leg or die he wins.

----------------------------------------
Commands:

!brokenboner			      - Explanation of the game
!bonercommands 			      - Bot command list
!currentboner 		    	  - Current onwer of the title "Broken Boner"
!timer 				          - The current time on the timer
!bet <number of minutes> 	  - Enter the pool with the number of minutes specified
!mybet				          - Displays your current bet
!betstats			          - Displays the lowest, highest and average of the bets and the number of people betting
!bonermods		           	  - Current authorised users

Authorised users only:
!setboner <name> 		      - Changes the current title holder to <name>
!openbets 		              - Allows the chat to start betting
!starttimer		           	  - Starts the timer and closes the betting
!stopttimer		          	  - Stops the timer
!closebets	          		  - Stops people from using !bet
!adduser <name>			      - Adds a user to the list of authorised users
!removeuser <name> 		      - Removes a user from the list of authorised users

----------------------------------------
Notes:


----------------------------------------
Upcoming features:

- Allow bets with seconds.
- Show statistics about previous winners, such as how many wins someone has or the average winning time.

----------------------------------------
Known bugs:

- The bot seems to stop working after a certain amount of inactivity (~10 minutes). As of now i have no idea why this happens...