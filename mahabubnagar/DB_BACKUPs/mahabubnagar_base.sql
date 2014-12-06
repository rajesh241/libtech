-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: mahabubnagar
-- ------------------------------------------------------
-- Server version	5.5.40-0ubuntu1

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
-- Table structure for table `blocks`
--

DROP TABLE IF EXISTS `blocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `isActive` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blocks`
--

LOCK TABLES `blocks` WRITE;
/*!40000 ALTER TABLE `blocks` DISABLE KEYS */;
INSERT INTO `blocks` VALUES (1,'Ghattu','36','14','057',1);
/*!40000 ALTER TABLE `blocks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ftoDetails`
--

DROP TABLE IF EXISTS `ftoDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ftoDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ftoNo` varchar(30) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `finyear` varchar(2) DEFAULT NULL,
  `isDownloaded` tinyint(1) DEFAULT '0',
  `isProcessed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ftoNo` (`ftoNo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ftoDetails`
--

LOCK TABLES `ftoDetails` WRITE;
/*!40000 ALTER TABLE `ftoDetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `ftoDetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ftoTransactionDetails`
--

DROP TABLE IF EXISTS `ftoTransactionDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `ftoNo` (`ftoNo`,`referenceNo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ftoTransactionDetails`
--

LOCK TABLES `ftoTransactionDetails` WRITE;
/*!40000 ALTER TABLE `ftoTransactionDetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `ftoTransactionDetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobcardDetails`
--

DROP TABLE IF EXISTS `jobcardDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobcardDetails`
--

LOCK TABLES `jobcardDetails` WRITE;
/*!40000 ALTER TABLE `jobcardDetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobcardDetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobcardRegister`
--

DROP TABLE IF EXISTS `jobcardRegister`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
  `govtJobcard` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `jobcard` (`jobcard`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobcardRegister`
--

LOCK TABLES `jobcardRegister` WRITE;
/*!40000 ALTER TABLE `jobcardRegister` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobcardRegister` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `musterTransactionDetails`
--

DROP TABLE IF EXISTS `musterTransactionDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `musterTransactionDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `musterNo` varchar(10) DEFAULT NULL,
  `finyear` varchar(2) DEFAULT NULL,
  `workCode` varchar(40) DEFAULT NULL,
  `musterIndex` tinyint(4) DEFAULT NULL,
  `name` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `jobcard` varchar(30) DEFAULT NULL,
  `daysWorked` tinyint(4) DEFAULT NULL,
  `dayWage` int(11) DEFAULT NULL,
  `totalWage` int(11) DEFAULT NULL,
  `accountNo` varchar(25) DEFAULT NULL,
  `bankNameOrPOName` varchar(40) DEFAULT NULL,
  `branchNameOrPOAddress` varchar(40) DEFAULT NULL,
  `branchCodeOrPOCode` varchar(20) DEFAULT NULL,
  `wagelistNo` varchar(20) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `creditedDate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `musterNo` (`musterNo`,`musterIndex`,`finyear`,`workCode`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `musterTransactionDetails`
--

LOCK TABLES `musterTransactionDetails` WRITE;
/*!40000 ALTER TABLE `musterTransactionDetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `musterTransactionDetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `musters`
--

DROP TABLE IF EXISTS `musters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `musters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `musterNo` varchar(10) DEFAULT NULL,
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
  `isProcessed` tinyint(1) DEFAULT '0',
  `isComplete` tinyint(1) DEFAULT '0',
  `isError` tinyint(1) DEFAULT '0',
  `isZeroAttendance` tinyint(1) DEFAULT '0',
  `lastProcessDate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `muster_unique_key` (`finyear`,`musterNo`,`workCode`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `musters`
--

LOCK TABLES `musters` WRITE;
/*!40000 ALTER TABLE `musters` DISABLE KEYS */;
/*!40000 ALTER TABLE `musters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `panchayats`
--

DROP TABLE IF EXISTS `panchayats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `panchayats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `jobcardCrawlDate` datetime DEFAULT NULL,
  `jobcardCrawlStatus` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `panchayats`
--

LOCK TABLES `panchayats` WRITE;
/*!40000 ALTER TABLE `panchayats` DISABLE KEYS */;
INSERT INTO `panchayats` VALUES (1,'Nandinne','36','14','057','001','2014-12-06 12:37:46',0),(2,'Kaloortimmanadoddi','36','14','057','002','2014-12-06 13:03:23',0),(3,'Thummalacheruvu','36','14','057','003','2014-12-06 13:03:52',0),(4,'Aloor','36','14','057','004','2014-12-06 13:04:33',0),(5,'Kuchinerla','36','14','057','005','2014-12-06 12:39:07',0),(6,'Chintalakunta','36','14','057','006','2014-12-06 12:39:47',0),(7,'Rayapuram','36','14','057','007','2014-12-06 13:08:57',0),(8,'Penchikalpadu','36','14','057','008','2014-12-06 12:40:50',0),(9,'Aragidda','36','14','057','009','2014-12-06 12:41:25',0),(10,'Ghattu','36','14','057','010','2014-12-06 12:42:11',0),(11,'Yallamdoddi','36','14','057','011','2014-12-06 13:09:55',0),(12,'Macherla','36','14','057','012','2014-12-06 12:43:46',0),(13,'Gorlakhandoddi','36','14','057','013','2014-12-06 12:44:44',0),(14,'Thappetlamorsu','36','14','057','014','2014-12-06 12:45:08',0),(15,'Mittadoddi','36','14','057','015','2014-12-06 12:45:41',0),(16,'Balgera','36','14','057','016','2014-12-06 12:46:22',0),(17,'Induvasi','36','14','057','017','2014-12-06 12:47:00',0),(18,'Boyalagudem','36','14','057','018','2014-12-06 12:47:53',0),(19,'Chagadona','36','14','057','019','2014-12-06 12:48:34',0),(20,'Lingapuram','36','14','057','020','2014-12-06 12:49:40',0),(21,'Mallampalli','36','14','057','021','2014-12-06 13:05:38',0),(22,'Mallapur','36','14','057','022','2014-12-06 12:50:20',0),(23,'Thummalapalli','36','14','057','023','2014-12-06 12:50:55',0),(24,'Yarsandoddi','36','14','057','024','2014-12-06 12:51:26',0);
/*!40000 ALTER TABLE `panchayats` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-12-06 13:15:17
