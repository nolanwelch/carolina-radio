# Carolina Radio

Turn your Spotify sessions into a shared radio experience with friends! Our app lets everyone add song requests to a communal pool, and tracks are chosen dynamically based on popularity and a bit of chance, creating a unique, synchronized playlist that brings everyone together in real time. Tune in, discover new favorites, and feel like you're all in the same room, no matter where you are.

## Inspiration

The radio has always been a great way to be exposed to new music, especially with students radio stations such as WXYC. Carolina Radio expands upon this, democratizing the music suggesting process.

## What it does

Carolina Radio takes in song submissions from across campus and creates a queue that anyone can listen in on. Songs are picked based on a combination of the amount of time since they were requested, the number of times they have been requested, and the amount of time since they were last played.

## How we built it

We built the frontend using React, hosting it on Cloudflare Pages for easy global distribution. The backend was built using Python and FastAPI combined with MongoDB Atlas for data storage. All of the management of user sessions and the connections with the Spotify API for playing songs is managed entirely by the backend.

## Challenges we ran into

The Spotify API was challenging to manage, as we had to manually control the user's queue and track our own record of songs that had been requested. In addition, we faced many difficulties with managing the queue and properly syncing it across all connected users.

## Accomplishments that we're proud of

A big accomplishment we are proud of is the management of our own authorization session system, managing the oauth login using Spotify from end to end.

## What we learned

We learned a lot more about the full stack web development process, and each used some new technologies that we hadn't used before. We also learned more about the fundamentals of user authentication and session handling.

## What's next for Carolina Radio

One big goal we have is to formally lock it down to just UNC Students, as well as to expand variations to other campuses, allowing other campuses to experience the shared music queue as well. Additionally, we would like to provide a spin-off feature that is designed for managing a queue for a party, using the same technology but with only one player.