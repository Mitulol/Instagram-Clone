PRAGMA foreign_keys = ON;

INSERT INTO users (username, fullname, email, filename, password)
VALUES
('awdeorio', 'Andrew DeOrio', 'awdeorio@umich.edu', 'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg',
 'sha512$34e94a05cdf247db92a84bc590950336$7eaca2b4169e042120f015666115856c717343f1c75d1c1bd1bf469bd1cd439eb152ccda6a0b8703706dfbcb861b3cef9208325c31f436e8edb9563f01176c48'),
('jflinn', "Jason Flinn", 'jflinn@umich.edu', '505083b8b56c97429a728b68f31b0b2a089e5113.jpg',
 'sha512$673d22398b0141c7929f987efee061e6$187dd68d62574a29b40513467cb5376849d6e7651dbd19850b853b912f44d940a42ef6bb96f4bafa82a6b40072ed980bfad377c65faa096281369210841f2b73'),
('michjc', 'Michael Cafarella', 'michjc@umich.edu', '5ecde7677b83304132cb2871516ea50032ff7a4f.jpg',
 'sha512$d7cde81ee4614141b68fbe8ff5fffa76$8b432b218b18554e58a949a40367a0d0e731dc8f8a46ecaa3ea0aca39169b3a97f12246d2840d6e9c32764907ed7b1951dfc16f213cb7fd4a6a96dc43f52f67b'),
('jag', 'H.V. Jagadish', 'jag@umich.edu', '73ab33bd357c3fd42292487b825880958c595655.jpg',
 'sha512$0b2b8d18beba4c2ba7dad0365d1dd885$130546cafab793f769a86607466fb07476b03c5de1f32f666c1e72e8b48b5e7e08494ec85ede12df72d259112bca3d5783983937361fe0aa2c341ae7bd0c2da4');

INSERT INTO posts (filename, owner)
VALUES
('122a7d27ca1d7420a1072f695d9290fad4501a41.jpg', 'awdeorio'),
('ad7790405c539894d25ab8dcf0b79eed3341e109.jpg', 'jflinn'),
('9887e06812ef434d291e4936417d125cd594b38a.jpg', 'awdeorio'),
('2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg', 'jag');

INSERT INTO likes (owner, postid)
VALUES
('awdeorio', 1),
('michjc', 1),
('jflinn', 1),
('awdeorio', 2),
('michjc', 2),
('awdeorio', 3);

INSERT INTO comments(owner, postid, text)
VALUES 
('awdeorio', 3, '#chickensofinstagram'),
('jflinn', 3, 'I <3 chickens'),
('michjc', 3, 'Cute overload!'),
('awdeorio', 2, 'Sick #crossword'),
('jflinn', 1, 'Walking the plank #chickensofinstagram'),
('awdeorio', 1, 'This was after trying to teach them to do a #crossword'),
('jag', 4, 'Saw this on the diag yesterday!');;

INSERT INTO following(username1, username2)
VALUES 
('awdeorio', 'jflinn'),
('awdeorio', 'michjc'),
('jflinn', 'awdeorio'),
('jflinn', 'michjc'),
('michjc', 'awdeorio'),
('michjc', 'jag'),
('jag', 'michjc');