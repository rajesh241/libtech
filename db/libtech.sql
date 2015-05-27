-- MySQL dump 10.13  Distrib 5.5.43, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: libtech
-- ------------------------------------------------------
-- Server version	5.5.43-0ubuntu0.12.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Broadcasts`
--

DROP TABLE IF EXISTS `Broadcasts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Broadcasts` (
  `bid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `lid` int(11) DEFAULT '0',
  `gid` int(11) DEFAULT '0',
  `tid` int(11) DEFAULT '0',
  `vid` int(11) DEFAULT '0',
  `processed` tinyint(1) DEFAULT '0',
  `tfileid` int(11) DEFAULT NULL,
  `minhour` int(11) DEFAULT NULL,
  `maxhour` int(11) DEFAULT NULL,
  `startDate` datetime DEFAULT NULL,
  `endDate` datetime DEFAULT NULL,
  `completed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`bid`)
) ENGINE=InnoDB AUTO_INCREMENT=211 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CompletedCalls`
--

DROP TABLE IF EXISTS `CompletedCalls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `CompletedCalls` (
  `ccid` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(255) DEFAULT NULL,
  `bid` int(11) DEFAULT NULL,
  `tid` int(11) DEFAULT NULL,
  `vid` int(11) DEFAULT NULL,
  `success` tinyint(1) DEFAULT '0',
  `ctime` datetime DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `debug` varchar(255) DEFAULT NULL,
  `callparams` varchar(1024) DEFAULT NULL,
  `vendorcid` varchar(20) DEFAULT NULL,
  `status` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`ccid`)
) ENGINE=InnoDB AUTO_INCREMENT=1130059 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Groups`
--

DROP TABLE IF EXISTS `Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Groups` (
  `gid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`gid`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `JobCardDetails`
--

DROP TABLE IF EXISTS `JobCardDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `JobCardDetails` (
  `jid` int(11) NOT NULL AUTO_INCREMENT,
  `jobcardno` varchar(255) DEFAULT NULL,
  `uid` int(11) DEFAULT NULL,
  PRIMARY KEY (`jid`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LocationType`
--

DROP TABLE IF EXISTS `LocationType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LocationType` (
  `ltid` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ltid`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Locations`
--

DROP TABLE IF EXISTS `Locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Locations` (
  `lid` int(11) NOT NULL AUTO_INCREMENT,
  `plid` int(11) DEFAULT '0',
  `name` varchar(255) DEFAULT NULL,
  `type` int(11) DEFAULT '1',
  PRIMARY KEY (`lid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Templates`
--

DROP TABLE IF EXISTS `Templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Templates` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `getplaylist` varchar(255) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`tid`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ToCall`
--

DROP TABLE IF EXISTS `ToCall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ToCall` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `vid` int(11) DEFAULT '0',
  `phone` varchar(255) DEFAULT NULL,
  `vendorcallid` int(11) DEFAULT NULL,
  `tid` int(11) DEFAULT '0',
  `retry` int(11) DEFAULT '10',
  `debug` varchar(255) DEFAULT NULL,
  `inprogress` tinyint(1) DEFAULT '0',
  `success` tinyint(1) DEFAULT '0',
  `callparams` varchar(1024) DEFAULT NULL,
  `bid` int(11) DEFAULT NULL,
  `successrate` int(11) DEFAULT NULL,
  `minhour` int(11) DEFAULT NULL,
  `maxhour` int(11) DEFAULT NULL,
  `callRequestTime` datetime DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB AUTO_INCREMENT=38366 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Users` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `lid` int(11) DEFAULT '1',
  `sid` int(11) DEFAULT NULL,
  `DND` int(11) DEFAULT '0',
  `alternate_phone` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=2715 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `UsersGroup`
--

DROP TABLE IF EXISTS `UsersGroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `UsersGroup` (
  `ugid` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `gid` int(11) DEFAULT NULL,
  PRIMARY KEY (`ugid`)
) ENGINE=InnoDB AUTO_INCREMENT=2709 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Vendors`
--

DROP TABLE IF EXISTS `Vendors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Vendors` (
  `vid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`vid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `addressbook`
--

DROP TABLE IF EXISTS `addressbook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `addressbook` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(10) NOT NULL,
  `region` varchar(10) NOT NULL,
  `district` varchar(40) DEFAULT NULL,
  `block` varchar(40) DEFAULT NULL,
  `panchayat` varchar(40) DEFAULT NULL,
  `jobcard` varchar(40) DEFAULT NULL,
  `pdsno` varchar(40) DEFAULT NULL,
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=2243 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `anekapalli_ab`
--

DROP TABLE IF EXISTS `anekapalli_ab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `anekapalli_ab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `caste` varchar(10) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `job_card` varchar(30) DEFAULT NULL,
  `block` varchar(40) DEFAULT NULL,
  `panchayat` varchar(40) DEFAULT NULL,
  `village` varchar(40) DEFAULT NULL,
  `successrate` int(11) DEFAULT '100',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4122 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apnrega_tocall`
--

DROP TABLE IF EXISTS `apnrega_tocall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apnrega_tocall` (
  `apnregaid` int(11) NOT NULL AUTO_INCREMENT,
  `household_code` bigint(20) DEFAULT NULL,
  `amount` bigint(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `payingagency` varchar(40) DEFAULT NULL,
  `panchayat` varchar(40) DEFAULT NULL,
  `epayorder` bigint(20) DEFAULT NULL,
  `epayorder2` bigint(20) DEFAULT NULL,
  `payorder_no` bigint(20) DEFAULT NULL,
  `worker_code` bigint(20) DEFAULT NULL,
  `name` varchar(60) DEFAULT NULL,
  `fto_no` bigint(20) DEFAULT NULL,
  `status` int(11) DEFAULT '0',
  `bankdate` varchar(40) DEFAULT NULL,
  `disbursed_date` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`apnregaid`)
) ENGINE=InnoDB AUTO_INCREMENT=522 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apvvu`
--

DROP TABLE IF EXISTS `apvvu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apvvu` (
  `uid` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `jobcard` varchar(255) DEFAULT NULL,
  `phone` varchar(255) NOT NULL,
  `alternate_phone` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  KEY `phone_idx` (`phone`),
  KEY `alternate_phone_idx` (`alternate_phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apvvuVG_ab`
--

DROP TABLE IF EXISTS `apvvuVG_ab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apvvuVG_ab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(10) DEFAULT NULL,
  `successrate` int(11) DEFAULT '100',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=468 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audioLibrary`
--

DROP TABLE IF EXISTS `audioLibrary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `audioLibrary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `callStatus`
--

DROP TABLE IF EXISTS `callStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `callStatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bid` int(11) NOT NULL,
  `success` tinyint(1) DEFAULT '0',
  `expired` tinyint(1) DEFAULT '0',
  `phone` varchar(10) DEFAULT NULL,
  `maxRetryFail` tinyint(1) DEFAULT '0',
  `attempts` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=480782 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chakri_ab`
--

DROP TABLE IF EXISTS `chakri_ab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chakri_ab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(15) DEFAULT NULL,
  `job_card` varchar(30) DEFAULT NULL,
  `name` varchar(70) DEFAULT NULL,
  `panchayat` varchar(40) DEFAULT NULL,
  `village` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1253 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chattis_ab`
--

DROP TABLE IF EXISTS `chattis_ab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chattis_ab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(15) DEFAULT NULL,
  `job_card` varchar(30) DEFAULT NULL,
  `panchayat` varchar(40) DEFAULT NULL,
  `habitation` varchar(40) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `relationname` varchar(100) DEFAULT NULL,
  `gp_code` varchar(5) DEFAULT NULL,
  `successrate` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3466 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exotelDetails`
--

DROP TABLE IF EXISTS `exotelDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exotelDetails` (
  `PhoneNumber` varchar(24) NOT NULL,
  `Circle` varchar(2) DEFAULT NULL,
  `CircleName` varchar(255) DEFAULT NULL,
  `Type` varchar(24) DEFAULT NULL,
  `Operator` varchar(2) DEFAULT NULL,
  `OperatorName` varchar(24) DEFAULT NULL,
  `DND` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`PhoneNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ghattuMissedCalls`
--

DROP TABLE IF EXISTS `ghattuMissedCalls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ghattuMissedCalls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phoneraw` varchar(20) DEFAULT NULL,
  `phone` varchar(10) DEFAULT NULL,
  `ctime` datetime DEFAULT NULL,
  `processed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=325 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ghattuMissedCallsLog`
--

DROP TABLE IF EXISTS `ghattuMissedCallsLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ghattuMissedCallsLog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `missedCallID` int(11) DEFAULT NULL,
  `phone` varchar(10) DEFAULT '',
  `ctime` datetime DEFAULT NULL,
  `ts` int(11) DEFAULT NULL,
  `jobcard` varchar(18) DEFAULT '',
  `workerID` varchar(20) DEFAULT '',
  `payOrderList` varchar(256) DEFAULT '',
  `name` varchar(30) DEFAULT '',
  `complaintNumber` varchar(10) DEFAULT '',
  `complaintDate` datetime DEFAULT NULL,
  `problemType` varchar(256) DEFAULT '',
  `periodInWeeks` int(11) DEFAULT '0',
  `remarks` blob,
  `currentStep` varchar(256) DEFAULT 'Call Pending',
  `closureReason` varchar(256) DEFAULT '',
  `htmlgen` tinyint(1) DEFAULT '1',
  `isUpdate` tinyint(1) DEFAULT '0',
  `finalStatus` varchar(10) DEFAULT 'open',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42901 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ghattu_ab`
--

DROP TABLE IF EXISTS `ghattu_ab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ghattu_ab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(15) DEFAULT NULL,
  `job_card` varchar(30) DEFAULT NULL,
  `panchayat` varchar(40) DEFAULT NULL,
  `village` varchar(40) DEFAULT NULL,
  `designation` varchar(40) DEFAULT NULL,
  `successrate` int(11) DEFAULT '100',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3142 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pdsresponse`
--

DROP TABLE IF EXISTS `pdsresponse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pdsresponse` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(15) DEFAULT NULL,
  `status` tinyint(1) DEFAULT '0',
  `message` varchar(128) DEFAULT NULL,
  `ctime` datetime DEFAULT NULL,
  `panchayat` varchar(50) DEFAULT NULL,
  `response` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=886 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pendingreport`
--

DROP TABLE IF EXISTS `pendingreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pendingreport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(20) DEFAULT NULL,
  `processed` tinyint(1) DEFAULT '0',
  `panchayatcode` varchar(10) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `places`
--

DROP TABLE IF EXISTS `places`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `places` (
  `pid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `ptid` int(11) DEFAULT NULL,
  `code` varchar(10) DEFAULT NULL,
  `parentpid` int(11) DEFAULT NULL,
  PRIMARY KEY (`pid`),
  KEY `ptid` (`ptid`),
  CONSTRAINT `places_ibfk_1` FOREIGN KEY (`ptid`) REFERENCES `placesType` (`ptid`)
) ENGINE=InnoDB AUTO_INCREMENT=320 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `placesType`
--

DROP TABLE IF EXISTS `placesType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `placesType` (
  `ptid` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ptid`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rscd_ab`
--

DROP TABLE IF EXISTS `rscd_ab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rscd_ab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(10) DEFAULT NULL,
  `successrate` int(11) DEFAULT '100',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1407 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rscdsms`
--

DROP TABLE IF EXISTS `rscdsms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rscdsms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(10) DEFAULT NULL,
  `smssent` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `smc`
--

DROP TABLE IF EXISTS `smc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smc` (
  `smc_id2` int(11) NOT NULL AUTO_INCREMENT,
  `School_Code` int(11) DEFAULT NULL,
  `Mobile_Number` varchar(255) DEFAULT NULL,
  `Mobile_Number_2` varchar(255) DEFAULT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `S/o_W/o` varchar(255) DEFAULT NULL,
  `Habitation` varchar(255) DEFAULT NULL,
  `Panchayat` varchar(255) DEFAULT NULL,
  `Mandal` varchar(255) DEFAULT NULL,
  `School` varchar(255) DEFAULT NULL,
  `Gender` varchar(255) DEFAULT NULL,
  `Age` int(11) DEFAULT NULL,
  `Occupation` varchar(255) DEFAULT NULL,
  `Is_Volunteer` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`smc_id2`)
) ENGINE=InnoDB AUTO_INCREMENT=381 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `telangana_r14_19`
--

DROP TABLE IF EXISTS `telangana_r14_19`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `telangana_r14_19` (
  `state` varchar(40) NOT NULL,
  `district` varchar(40) NOT NULL,
  `mandal` varchar(40) NOT NULL,
  `panchayat` varchar(40) NOT NULL,
  `habitation` varchar(40) NOT NULL,
  `paying_agency` varchar(40) NOT NULL,
  `tsp` varchar(40) NOT NULL,
  `report_date` varchar(40) NOT NULL,
  `epayorder_no` bigint(20) NOT NULL,
  `epayorder_created_date` varchar(40) NOT NULL,
  `epayorder_sent_to_pa_date` varchar(40) NOT NULL,
  `uid_no` varchar(40) NOT NULL,
  `payorder_no` bigint(20) NOT NULL,
  `household_code` bigint(20) NOT NULL,
  `worker_code` bigint(20) NOT NULL,
  `wageseeker_name` varchar(40) NOT NULL,
  `paying_agency_account_no` bigint(20) NOT NULL,
  `days_worked` bigint(20) NOT NULL,
  `payorder_amount` bigint(20) NOT NULL,
  `rrn_number` bigint(20) NOT NULL,
  `payment_mode` varchar(40) NOT NULL,
  `disbursement_date_and_time` varchar(40) NOT NULL,
  `disbursement_data_uploaded_time` varchar(40) NOT NULL,
  `disbursed_amount` bigint(20) NOT NULL,
  PRIMARY KEY (`epayorder_no`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tring_ap_numbers`
--

DROP TABLE IF EXISTS `tring_ap_numbers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tring_ap_numbers` (
  `number` int(11) DEFAULT NULL,
  `fileid` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-05-27 17:46:23
