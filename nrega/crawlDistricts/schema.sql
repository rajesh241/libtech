DROP TABLE IF EXISTS `blocks`;
CREATE TABLE `blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) DEFAULT NULL,
  `censusName` varchar(40) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `pdsBlockCode` varchar(2) DEFAULT NULL,
  `isRequired` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `BLOCKCODE` (`blockCode`)
);


DROP TABLE IF EXISTS `ftoDetails`;
CREATE TABLE `ftoDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ftoNo` varchar(50) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `finyear` varchar(2) DEFAULT NULL,
  `isDownloaded` tinyint(1) DEFAULT '0',
  `isProcessed` tinyint(1) DEFAULT '0',
  `statusDownloadDate` datetime DEFAULT '2015-12-12 00:00:00',
  `isStatusDownloaded` tinyint(1) DEFAULT '0',
  `isStatusProcessed` tinyint(1) DEFAULT '0',
  `incorrectPOFile` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `FTONO` (`ftoNo`)
) ;


DROP TABLE IF EXISTS `ftoTransactionDetails`;
CREATE TABLE `ftoTransactionDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ftoNo` varchar(30) DEFAULT NULL,
  `referenceNo` varchar(40) DEFAULT NULL,
  `jobcard` varchar(30) DEFAULT NULL,
  `applicantName` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `primaryAccountHolder` varchar(50) DEFAULT NULL,
  `accountNo` varchar(25) DEFAULT NULL,
  `wagelistNo` varchar(20) DEFAULT NULL,
  `transactionDate` datetime DEFAULT NULL,
  `processedDate` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `rejectionReason` varchar(50) DEFAULT NULL,
  `utrNo` varchar(20) DEFAULT NULL,
  `creditedAmount` int(11) DEFAULT NULL,
  `bankCode` varchar(10) DEFAULT NULL,
  `IFSCCode` varchar(15) DEFAULT NULL,
  `finyear` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ftoNo` (`ftoNo`,`referenceNo`)
);


DROP TABLE IF EXISTS `jobcardDetails`;
CREATE TABLE `jobcardDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jobcard` varchar(30) DEFAULT NULL,
  `applicantNo` tinyint(4) DEFAULT NULL,
  `age` tinyint(4) DEFAULT NULL,
  `applicantName` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `gender` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `accountNo` varchar(25) DEFAULT NULL,
  `aadharNo` varchar(30) DEFAULT NULL,
  `accountNoError` tinyint(1) DEFAULT '0',
  `nameHasError` tinyint(1) DEFAULT '0',
  `primaryAccountHolder` varchar(50) DEFAULT NULL,
  `bankNameOrPOName` varchar(40) DEFAULT NULL,
  `bankCode` varchar(10) DEFAULT NULL,
  `branchNameOrPOAddress` varchar(40) DEFAULT NULL,
  `branchCodeOrPOCode` varchar(20) DEFAULT NULL,
  `IFSCCodeOrEMOCode` varchar(15) DEFAULT NULL,
  `MICRCodeOrSanchayCode` varchar(15) DEFAULT NULL,
  `accountFrozen` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `jobcardApplicant` (`jobcard`,`applicantNo`)
);

DROP TABLE IF EXISTS `jobcardRegister`;
CREATE TABLE `jobcardRegister` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jobcard` varchar(30) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `isDownloaded` tinyint(1) DEFAULT '0',
  `isProcessed` tinyint(1) DEFAULT '0',
  `headOfFamily` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `fatherHusbandName` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `issueDate` datetime DEFAULT NULL,
  `caste` varchar(10) DEFAULT NULL,
  `village` varchar(40) DEFAULT NULL,
  `isBPL` tinyint(1) DEFAULT '0',
  `issueDateError` tinyint(1) DEFAULT '0',
  `jobcardError` tinyint(1) DEFAULT '0',
  `workerDetailsAbsent` tinyint(1) DEFAULT '0',
  `nameHasError` tinyint(1) DEFAULT '0',
  `jcNumber` smallint(6) DEFAULT NULL,
  `phone` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `jobcard` (`jobcard`)
);

DROP TABLE IF EXISTS `musters`;
CREATE TABLE `musters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `musterNo` varchar(50) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `finyear` varchar(2) DEFAULT NULL,
  `musterType` varchar(5) DEFAULT '10',
  `workCode` varchar(40) DEFAULT NULL,
  `workName` varchar(1024) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `dateFrom` datetime DEFAULT NULL,
  `dateTo` datetime DEFAULT NULL,
  `isDownloaded` tinyint(1) DEFAULT '0',
  `isZeroAttendance` tinyint(1) DEFAULT '0',
  `crawlDate` datetime DEFAULT NULL,
  `downloadAttemptDate` datetime DEFAULT '2015-08-28 00:00:00',
  `wdProcessed` tinyint(1) DEFAULT '0',
  `wdError` tinyint(1) DEFAULT '0',
  `wdComplete` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `MUSTERKEY` (`finyear`,`musterNo`,`blockCode`)
);


DROP TABLE IF EXISTS `panchayats`;
CREATE TABLE `panchayats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `jobcardCrawlDate` datetime DEFAULT NULL,
  `jobcardCrawlStatus` tinyint(1) DEFAULT '0',
  `isSurvey` tinyint(1) DEFAULT '0',
  `totalJobcards` int(11) DEFAULT '0',
  `totalWorkers` int(11) DEFAULT '0',
  `totalMobiles` int(11) DEFAULT '0',
  `isRequired` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `PANCHAYATKEY` (`blockCode`,`panchayatCode`)

);


DROP TABLE IF EXISTS `reportQueries`;
CREATE TABLE `reportQueries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(20) DEFAULT NULL,
  `title` varchar(512) DEFAULT NULL,
  `dbname` varchar(50) DEFAULT NULL,
  `selectClause` varchar(1024) DEFAULT NULL,
  `whereClause` varchar(1024) DEFAULT NULL,
  `orderClause` varchar(1024) DEFAULT NULL,
  `groupClause` varchar(1024) DEFAULT NULL,
  `linkIndex` varchar(256) DEFAULT NULL,
  `linkType` varchar(256) DEFAULT NULL,
  `limitResults` tinyint(1) DEFAULT '1',
  `finyearFilter` varchar(256) DEFAULT '  ',
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `workDetails`;
CREATE TABLE `workDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `blockName` varchar(40) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatName` varchar(40) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `finyear` varchar(2) DEFAULT NULL,
  `musterIndex` tinyint(4) DEFAULT NULL,
  `name` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `jobcard` varchar(30) DEFAULT NULL,
  `jcNumber` int DEFAULT NULL,
  `musterNo` varchar(50) DEFAULT NULL,
  `workCode` varchar(40) DEFAULT NULL,
  `workName` varchar(1024) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `dateFrom` datetime DEFAULT NULL,
  `dateTo` datetime DEFAULT NULL,
  `daysWorked` tinyint(4) DEFAULT NULL,
  `dayWage` int(11) DEFAULT NULL,
  `totalWage` int(11) DEFAULT NULL,
  `accountNo` varchar(25) DEFAULT NULL,
  `wagelistNo` varchar(20) DEFAULT NULL,
  `bankNameOrPOName` varchar(40) DEFAULT NULL,
  `branchNameOrPOAddress` varchar(40) DEFAULT NULL,
  `branchCodeOrPOCode` varchar(20) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `creditedDate` datetime DEFAULT NULL,
  `isBank` tinyint(1) DEFAULT '0',
  `isPost` tinyint(1) DEFAULT '0',
  `rejectionReason` varchar(50) DEFAULT NULL,
  `ftoEventDate` datetime DEFAULT NULL,
  `ftoEvent` varchar(2048) DEFAULT NULL,
  `ftoOffice` varchar(1024) DEFAULT NULL,
  `ftoFileid` varchar(2048) DEFAULT NULL,
  `updateDate` datetime DEFAULT NULL,
  `createDate` datetime DEFAULT NULL,
  `ftoNo` varchar(30) DEFAULT NULL,
  `ftoNoUpdated` tinyint(1) DEFAULT '0',
  `primaryAccountHolder` varchar(50) DEFAULT NULL,
  `paymentDate` datetime DEFAULT NULL,
  `ftoMatchStatus` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mtkey` (`musterNo`,`musterIndex`,`finyear`,`blockCode`)
);
