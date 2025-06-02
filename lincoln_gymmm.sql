-- Drop existing tables if they exist to avoid conflicts
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS contact;
DROP TABLE IF EXISTS groupclass_booking;
DROP TABLE IF EXISTS groupclasses_session;
DROP TABLE IF EXISTS groupclasses;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS membership;


DROP TABLE IF EXISTS specializedclass_booking;
DROP TABLE IF EXISTS specializedclass_session;
DROP TABLE IF EXISTS specializedclasses;
DROP TABLE IF EXISTS trainer;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS user;
CREATE TABLE `user` (
  `userid` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `roles` varchar(20) NOT NULL,
  PRIMARY KEY (`userid`)
); 



INSERT INTO `user` VALUES (1,'amy','trainer'),(2,'prince','trainer'),(3,'john','trainer'),(4,'emily','trainer'),(5,'michael','trainer'),(6,'sarah','trainer'),(7,'christopher','trainer'),(8,'jessica','trainer'),(9,'daniel','trainer'),(10,'david','trainer'),(11,'stephanie','member'),(12,'nicholas','member'),(13,'amanda','member'),(14,'tyler','member'),(15,'heather','member'),(16,'ryan','member'),(17,'alyssa','member'),(18,'sim','admin');

CREATE TABLE `member` (
  `member_id` int NOT NULL AUTO_INCREMENT,
  `firstname` varchar(45) NOT NULL,
  `lastname` varchar(45) NOT NULL,
  `mobile` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `street` varchar(45) NOT NULL,
  `suburb` varchar(45) NOT NULL,
  `city` varchar(45) NOT NULL,
  `postalcode` varchar(45) NOT NULL,
  `subscription_status` varchar(20) NOT NULL,
  `userid` int NOT NULL,
  `join_date` date DEFAULT NULL,
  PRIMARY KEY (`member_id`),
  KEY `fk_memberuser` (`userid`),
  CONSTRAINT `fk_memberuser` FOREIGN KEY (`userid`) REFERENCES `user` (`userid`)
);



INSERT INTO `member` VALUES (101,'Stephanie','Hernandez','98764567','steph.dez123@gmail.com','54 Lanes Dr','Rolleston','Christchurch','79077','0',11,'2023-01-10'),(102,'Nicholas','Moore','2030400383839','nicholas.moore@ymail.com','Kemble Drive','Sydenham','Christchurch','7513','1',12,'2023-01-20'),(103,'Amanda','Martinn','542478905','martin.amanda123@hotmail.com','38 Southampton Street','Sydenham','Christchurch','8024','1',13,'2023-01-25'),(104,'Tyler','Jack','5490789611','tyler.jackson@gmail.com','32 Martin St','Sydenham','Hastings','8025','0',14,'2023-02-15'),(105,'Heather','Lee','98769178','lee.heather@gmail.com','65 Selwyn Street','Sydney','Christchurch','7079','0',15,'2023-02-21'),(106,'Ryan','Perez','70400397','ryanperez123@hotmail.com','34 Tennyson St','Cashmere','Christchurch','7095','0',16,'2023-02-22');


CREATE TABLE `trainer` (
  `trainer_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `mobile` int NOT NULL,
  `speciality` varchar(45) NOT NULL,
  `userid` int NOT NULL,
  PRIMARY KEY (`trainer_id`),
  KEY `userid` (`userid`),
  CONSTRAINT `trainer_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `user` (`userid`)
); 



INSERT INTO `trainer` VALUES (1001,'Amy','Jack','amy.jackson123@ymail.com',24356789,'Nutrition',1),(1002,'Prince','Singhal','princesinghal12@gmail.com',20400398,'Weight Loss',2),(1003,'John','Smith','smith.john@hotmail.com',22504786,'Yoga',3),(1004,'Emily','Johnson','emilyjohnson.ss@gmail.com',36754894,'Zumba',4),(1005,'Michael','Williams','williamstraining@gmail.com',45367892,'BodyPump',5),(1006,'Sarah','Brown','sarah.brown456@ymail.com',1234569,'Aerobics',6),(1007,'Christopher','Jones','jones.chris123@gmail.com',22348964,'Sprint',7),(1008,'Jesica','Gracia','graciafitness@gmail.com',75678932,'BodyBalance',8),(1009,'Daniel','Davis','davisthetrainer@gmail.com',987275789,'The Trip',9),(1010,'David','Martinez','david.martinez901@ymail.com',869054673,'Cardio',10);

CREATE TABLE `groupclasses` (
  `groupclasses_id` int NOT NULL AUTO_INCREMENT,
  `classname` varchar(45) NOT NULL,
  `class_description` varchar(120) NOT NULL,
  `trainer_id` int NOT NULL,
  PRIMARY KEY (`groupclasses_id`),
  KEY `trainer_id` (`trainer_id`),
  CONSTRAINT `groupclasses_ibfk_1` FOREIGN KEY (`trainer_id`) REFERENCES `trainer` (`trainer_id`)
); 




INSERT INTO `groupclasses` VALUES (101,'Yoga','daily scheduled at 9 am',1003),(102,'Nutrition','want advice for healthy body, book appointment everyday from 10 am to 2pm..',1001),(103,'Weight loss','get rid of the belly bulge, take classes on weight loss on mondays at 9am',1002),(104,'Sprint','build endurancee and become faster by taking claases on fridays every evening from 5pm to 6 pm.',1007),(105,'The Trip','engage yourself in full body workout, classes every saturday and sunday. From 7pm onwards.',1009),(106,'BodyPump','want to gain muscle, join us on every tuesday at 6pm.',1005),(107,'Zumba','Join zumba classes on wednesdays at 2pm.',1004),(108,'Aerobics','burn calories and become slim , classes every thurday evening from 5 pm.',1006),(109,'BodyBalance','Build body strength, classes every sunday from 10am.',1008),(110,'Cardio','Join us for cardio exercises every monday from 8 am.',1010);

CREATE TABLE `groupclasses_session` (
  `session_id` int NOT NULL AUTO_INCREMENT,
  `groupclasses_id` int NOT NULL,
  `class_time` time NOT NULL,
  `class_date` date NOT NULL,
  `class_capacity` int NOT NULL,
  PRIMARY KEY (`session_id`),
  KEY `groupclasses_id` (`groupclasses_id`),
  CONSTRAINT `groupclasses_session_ibfk_1` FOREIGN KEY (`groupclasses_id`) REFERENCES `groupclasses` (`groupclasses_id`),
  CONSTRAINT `chk_class_capacity` CHECK ((`class_capacity` <= 30))
); 





INSERT INTO `groupclasses_session` VALUES (1,102,'11:00:00','2023-05-11',24),(2,105,'20:00:00','2023-04-26',27),(3,101,'09:00:00','2023-04-05',27),(4,103,'09:00:00','2023-04-17',28),(5,104,'17:00:00','2023-05-10',27),(6,106,'18:00:00','2023-04-01',29),(7,107,'14:00:00','2023-04-11',28),(8,108,'17:00:00','2023-04-21',29),(9,109,'10:00:00','2023-04-20',29),(10,110,'08:00:00','2023-04-15',28);



CREATE TABLE `groupclass_booking` (
  `groupclass_bookingid` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `member_id` int NOT NULL,
  PRIMARY KEY (`groupclass_bookingid`),
  KEY `member_id` (`member_id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `groupclass_booking_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`),
  CONSTRAINT `groupclass_booking_ibfk_2` FOREIGN KEY (`session_id`) REFERENCES `groupclasses_session` (`session_id`)
); 





INSERT INTO `groupclass_booking` VALUES (10001,1,105),(10002,2,101),(10003,7,103),(10004,1,101),(10005,5,101),(10006,10,101),(10007,10,103),(10008,4,103),(10009,4,104),(10010,5,104),(10011,1,105),(10012,3,105),(10013,5,102),(10014,6,105),(10015,7,105),(10016,7,105),(10017,2,101),(10018,2,101),(10019,1,101),(10020,3,101),(10021,1,101),(10022,1,105),(10023,1,105),(10026,8,105),(10027,3,105),(10028,2,105),(10029,9,104);








CREATE TABLE `specializedclasses` (
  `specializedclasses_id` int NOT NULL AUTO_INCREMENT,
  `class_type` varchar(45) NOT NULL,
  `class_desc` varchar(255) NOT NULL,
  `trainer_id` int NOT NULL,
  `schedule` varchar(255) DEFAULT NULL,
  `pricing` decimal(10,2) NOT NULL,
  PRIMARY KEY (`specializedclasses_id`),
  KEY `trainer_id` (`trainer_id`),
  CONSTRAINT `specializedclasses_ibfk_1` FOREIGN KEY (`trainer_id`) REFERENCES `trainer` (`trainer_id`)
); 



INSERT INTO `specializedclasses` VALUES (500,'Pilates','Pull out your gym mat and get ready to do a series of movements that will stabilize and strengthen your core.',1004,'Every wednesday 2PM',50.00),(501,'Spin Cycle','We love to mix it up at Remix. With each instructor you’ll find that they bring their unique style and spin to our cycling classes. You’ll find an incredible smooth ride with our Schwinn Bikes that can accommodate both clip in cycle shoes OR sneakers. ',1001,'Monday mornings at 9AM',60.00),(502,'Combination Classes','If you’re looking for efficiency, take one of our combination classes that include cardio, strength and flexibility. ',1009,'Sunday special sessions at 8AM',100.00),(503,'Specific Focused Class','If you’re looking to focus on a specific body part, like your core or your arms, these classes are for you! ',1005,'Every Saturday evenings at 7PM',80.00),(505,'Cardio Classes','If you’re looking to build endurance and strengthen your heart and lunges, try one of our cardio classes',1001,'Tuesday evenings 6PM to 7PM',40.00),(506,'Strength Training Classes','If you’re looking for a low impact workout that’ll focus on body composition and building your strength, then try one of our strength training classes. ',1007,'Thursday morning at 10AM',50.00),(507,'BootCamp','Boot camp workouts include a range of cardio, strength training, and speed exercises all in one session',1006,'Friday evenings 7PM',70.00),(508,'Zumba','This dance class features high- and low-intensity intervals that help improve cardiovascular fitness while also enhancing balance, coordination, agility.',1002,'Weekends evenings 6PM',90.00);


CREATE TABLE `specializedclass_session` (
  `specializedclass_sessionid` int NOT NULL AUTO_INCREMENT,
  `specializedclasses_id` int NOT NULL,
  `specializedclass_time` time NOT NULL,
  `specializedclass_date` date NOT NULL,
  PRIMARY KEY (`specializedclass_sessionid`),
  KEY `specializedclasses_id` (`specializedclasses_id`),
  CONSTRAINT `specializedclass_session_ibfk_1` FOREIGN KEY (`specializedclasses_id`) REFERENCES `specializedclasses` (`specializedclasses_id`)
); 



INSERT INTO `specializedclass_session` VALUES (1,502,'08:00:00','2023-03-27'),(2,507,'19:00:00','2023-03-28'),(3,505,'18:00:00','2023-04-18'),(4,501,'09:00:00','2023-03-25'),(5,501,'09:00:00','2023-03-26');

CREATE TABLE `specializedclass_booking` (
  `specializedclass_bookingid` int NOT NULL AUTO_INCREMENT,
  `specializedclass_sessionid` int NOT NULL,
  `member_id` int NOT NULL,
  PRIMARY KEY (`specializedclass_bookingid`),
  KEY `member_id` (`member_id`),
  KEY `specializedclass_sessionid` (`specializedclass_sessionid`),
  CONSTRAINT `specializedclass_booking_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`),
  CONSTRAINT `specializedclass_booking_ibfk_2` FOREIGN KEY (`specializedclass_sessionid`) REFERENCES `specializedclass_session` (`specializedclass_sessionid`)
); 




INSERT INTO `specializedclass_booking` VALUES (101,2,102),(102,1,103),(103,3,103),(104,2,101),(105,2,103),(107,3,101),(108,1,101),(109,1,101),(110,1,101),(111,2,101),(112,3,101),(113,2,101),(114,3,101),(115,5,105),(116,3,104),(117,2,104),(118,4,105),(119,4,105),(120,4,105),(121,2,101),(122,3,101),(123,4,104),(124,2,101),(125,1,102),(126,1,101),(127,3,101),(128,1,101),(129,4,105),(130,4,105),(131,3,105),(132,4,105),(157,4,105),(158,4,105),(159,2,105),(160,2,105),(161,1,105),(162,4,105),(163,2,105),(164,3,105),(165,3,104),(166,3,105),(167,3,105),(168,3,105),(169,4,105),(170,1,105),(171,2,105),(172,2,105),(173,4,105),(174,1,105),(175,2,105),(176,4,105),(177,2,105),(178,3,102),(179,3,102),(180,3,102),(181,3,102),(182,3,104),(183,3,104),(184,3,104),(223,3,104),(224,4,103),(225,3,104),(226,1,104),(227,2,104),(228,1,104),(229,2,104),(230,1,104),(231,2,104),(232,2,104),(233,3,104),(234,4,104),(235,4,104),(236,3,104),(237,2,105),(238,3,105);


CREATE TABLE `payment` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `payment_date` date NOT NULL,
  `payment_amount` float NOT NULL,
  `specializedclass_bookingid` int NOT NULL,
  PRIMARY KEY (`payment_id`),
  KEY `member_id` (`member_id`),
  KEY `fk_paymentbooking` (`specializedclass_bookingid`),
  CONSTRAINT `fk_paymentbooking` FOREIGN KEY (`specializedclass_bookingid`) REFERENCES `specializedclass_booking` (`specializedclass_bookingid`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`)
); 



INSERT INTO `payment` VALUES (1,103,'2023-02-27',70,102),(2,101,'2023-03-24',40,122),(3,101,'2023-03-24',40,122),(4,101,'2023-03-24',100,110),(5,101,'2023-03-24',40,111),(6,104,'2023-03-25',60,123),(7,104,'2023-03-25',60,123),(8,104,'2023-03-25',60,123),(9,104,'2023-03-25',40,116),(10,101,'2023-03-25',70,124),(11,102,'2023-03-26',40,121),(12,101,'2022-12-22',60,124),(13,103,'2022-11-20',70,125),(14,102,'2022-07-14',100,120),(15,103,'2022-04-13',60,119),(16,101,'2023-03-28',40,108),(17,105,'2023-03-28',60,129),(19,104,'2023-03-30',0,117),(20,104,'2023-03-30',0,117),(21,104,'2023-03-30',0,226),(22,104,'2023-03-30',0,227),(23,104,'2023-03-30',0,228),(24,104,'2023-03-30',0,123),(25,104,'2023-03-30',0,230),(26,104,'2023-03-30',140,231),(27,104,'2023-03-30',140,231),(28,104,'2023-03-30',120,165),(29,104,'2023-03-30',240,123),(30,104,'2023-03-30',40,165),(31,104,'2023-03-30',40,165),(32,104,'2023-03-30',40,165),(33,104,'2023-03-30',40,165),(34,104,'2023-03-30',40,165),(35,104,'2023-03-30',40,165),(36,104,'2023-03-30',40,236),(37,105,'2023-03-30',70,237),(38,105,'2023-03-30',40,238);


CREATE TABLE `membership` (
  `membership_id` int NOT NULL AUTO_INCREMENT,
  `payment_date` date NOT NULL,
  `payment_amount` float NOT NULL,
  `member_id` int NOT NULL,
  PRIMARY KEY (`membership_id`),
  KEY `member_id_idx` (`member_id`),
  CONSTRAINT `fk_member_id` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`)
); 





INSERT INTO `membership` VALUES (1,'2023-03-20',60,102),(2,'2023-03-25',70,105),(3,'2023-02-28',50,101);
CREATE TABLE `contact` (
  `contactid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `mobile` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `message` varchar(255) NOT NULL,
  PRIMARY KEY (`contactid`)
); 



INSERT INTO `contact` VALUES (1,'Simranpreet simran','1234569','sim@gmail.com','Hi'),(2,'Karen','223467839','sarah@ggmail.com','Hi I want to know about exercise classes.'),(3,'Nicholas','676476','nichmoo@gmail.com','Hi');





CREATE TABLE `attendance` (
  `attendance_id` int NOT NULL AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `class_date` date NOT NULL,
  `swipe_in` time NOT NULL,
  `swipe_out` time NOT NULL,
  `category` varchar(20) NOT NULL,
  PRIMARY KEY (`attendance_id`),
  KEY `member_id` (`member_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`)
); 



INSERT INTO `attendance` VALUES (100,103,'2023-02-27','19:00:00','20:00:00','Personal Coaching'),(101,104,'2023-03-13','11:00:00','12:00:00','Group Class'),(102,103,'2023-03-16','19:00:00','20:00:00','Personal Coaching');
