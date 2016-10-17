DROP TABLE IF EXISTS `workDetails`;
CREATE TABLE `workDetails` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `blockName` varchar(40) DEFAULT NULL,
  `panchayatName` varchar(40) DEFAULT NULL,
 

  `finyear` varchar(2) DEFAULT NULL,
  `musterIndex` tinyint(4) DEFAULT NULL,
  `name` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `aadharNo` varchar(30) DEFAULT NULL,
  `jobcard` varchar(30) DEFAULT NULL,
  `jcNumber` bigint(20) DEFAULT NULL,
  `musterNo` varchar(50) DEFAULT NULL,
  `workCode` varchar(40) DEFAULT NULL,
  `workName` varchar(1024) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `daysWorked` tinyint(4) DEFAULT NULL,
  `dayWage` int(11) DEFAULT NULL,
  `totalWage` int(11) DEFAULT NULL,
  `accountNo` varchar(25) DEFAULT NULL,
  `wagelistNo` varchar(20) DEFAULT NULL,
  `bankNameOrPOName` varchar(40) DEFAULT NULL,
  `branchNameOrPOAddress` varchar(40) DEFAULT NULL,
  `branchCodeOrPOCode` varchar(20) DEFAULT NULL,
  `musterStatus` varchar(20) DEFAULT NULL,
  
  
 
  `dateFrom` datetime DEFAULT NULL,
  `dateTo` datetime DEFAULT NULL,
  `firstSignatoryDate` datetime DEFAULT NULL,
  `secondSignatoryDate` datetime DEFAULT NULL,
  `transactionDate` datetime DEFAULT NULL,
  `bankProcessedDate` datetime DEFAULT NULL,
  `processedDate` datetime DEFAULT NULL,
  `paymentDate` datetime DEFAULT NULL,
  `creditedDate` datetime DEFAULT NULL,

  `ftoMatchStatus` varchar(40) DEFAULT NULL,
  `jobcardRegisterMatchStatus` varchar(40) DEFAULT NULL, 
  `ftoNo` varchar(30) DEFAULT NULL,
  `primaryAccountHolder` varchar(50) DEFAULT NULL,
  `rejectionReason` varchar(50) DEFAULT NULL,
  `accountType` varchar(100)  DEFAULT NULL,
  `applicantNo` tinyint DEFAULT NULL,

  `updateDate` datetime DEFAULT NULL,
  `createDate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mtkey` (`musterNo`,`musterIndex`,`finyear`,`blockCode`)
);
