CREATE TABLE `blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `blockname` varchar(40) DEFAULT NULL,
  `rawBlockName` varchar(40) DEFAULT NULL,
  `districtName` varchar(40) DEFAULT NULL,
  `rawDistrictName` varchar(40) DEFAULT NULL,
  `stateName` varchar(40) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `fullBlockCode` varchar(7) DEFAULT NULL,
  `pdsBlockCode` varchar(2) DEFAULT NULL,
  `isRequired` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `BLOCKCODE` (`fullBlockCode`)
);
