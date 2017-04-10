CREATE TABLE `phoneBook` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(10) DEFAULT NULL,
  `fpsCode` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY  (`phone`)
);

