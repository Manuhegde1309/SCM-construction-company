-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: localhost    Database: dbms_project_testing
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Admin`
--

DROP TABLE IF EXISTS `Admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Admin` (
  `Admin_id` varchar(50) NOT NULL,
  `Firstname` varchar(50) NOT NULL,
  `Middlename` varchar(50) DEFAULT NULL,
  `Lastname` varchar(50) NOT NULL,
  `Password` varchar(255) NOT NULL,
  PRIMARY KEY (`Admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Admin`
--

LOCK TABLES `Admin` WRITE;
/*!40000 ALTER TABLE `Admin` DISABLE KEYS */;
INSERT INTO `Admin` VALUES ('admf31','Mohammed','Furqaan','Patel','$argon2id$v=19$m=65536,t=3,p=4$6kwg2lMMT0w5yJESDBYsug$h8cBH8b7FC+zCjYFqRgXJnZ2Lm85Jb/txoU18rq81Ek'),('admh13','Manu','Narayan','Hegde','$argon2id$v=19$m=65536,t=3,p=4$TM5cRyMrORyRSGG3Ob0hjQ$hM/jQe6wfR/8P+aM2K2lNYO/HLg4bQKslhACblOs2n8');
/*!40000 ALTER TABLE `Admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Construction_Company`
--

DROP TABLE IF EXISTS `Construction_Company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Construction_Company` (
  `Construction_Company_id` varchar(50) NOT NULL,
  `Construction_Company_name` varchar(100) NOT NULL,
  `Admin_id` varchar(50) DEFAULT NULL,
  `Cash_Balance` decimal(20,2) DEFAULT '10000000.00',
  PRIMARY KEY (`Construction_Company_id`),
  UNIQUE KEY `Construction_Company_name` (`Construction_Company_name`),
  KEY `Admin_id` (`Admin_id`),
  CONSTRAINT `Construction_Company_ibfk_1` FOREIGN KEY (`Admin_id`) REFERENCES `Admin` (`Admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Construction_Company`
--

LOCK TABLES `Construction_Company` WRITE;
/*!40000 ALTER TABLE `Construction_Company` DISABLE KEYS */;
INSERT INTO `Construction_Company` VALUES ('ccpes1','pes','admh13',10000000.00),('ccpg1','Prestige','admf31',10000000.00);
/*!40000 ALTER TABLE `Construction_Company` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Product_info`
--

DROP TABLE IF EXISTS `Product_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Product_info` (
  `Product_id` varchar(50) NOT NULL,
  `Product_name` varchar(100) NOT NULL,
  `Product_price` decimal(10,2) NOT NULL,
  `Supplier_Company_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Product_id`),
  KEY `Supplier_Company_id` (`Supplier_Company_id`),
  CONSTRAINT `Product_info_ibfk_1` FOREIGN KEY (`Supplier_Company_id`) REFERENCES `Supplier_Company` (`Supplier_Company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Product_info`
--

LOCK TABLES `Product_info` WRITE;
/*!40000 ALTER TABLE `Product_info` DISABLE KEYS */;
INSERT INTO `Product_info` VALUES ('cmt1','CEMENT',2000.00,'sca2b1'),('fe35','IRON',100.00,'sca2b1'),('fe45','IRON',50.00,'scpes1');
/*!40000 ALTER TABLE `Product_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Shipment_Company`
--

DROP TABLE IF EXISTS `Shipment_Company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Shipment_Company` (
  `Shipment_Company_id` varchar(50) NOT NULL,
  `Supplier_Company_name` varchar(100) NOT NULL,
  PRIMARY KEY (`Shipment_Company_id`),
  UNIQUE KEY `Supplier_Company_name` (`Supplier_Company_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Shipment_Company`
--

LOCK TABLES `Shipment_Company` WRITE;
/*!40000 ALTER TABLE `Shipment_Company` DISABLE KEYS */;
INSERT INTO `Shipment_Company` VALUES ('DHL','DHL Group'),('FDX','FedEx Corp');
/*!40000 ALTER TABLE `Shipment_Company` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Supplier_Company`
--

DROP TABLE IF EXISTS `Supplier_Company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Supplier_Company` (
  `Supplier_Company_id` varchar(50) NOT NULL,
  `Supplier_Company_name` varchar(100) NOT NULL,
  `Password` varchar(255) NOT NULL,
  PRIMARY KEY (`Supplier_Company_id`),
  UNIQUE KEY `Supplier_Company_name` (`Supplier_Company_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Supplier_Company`
--

LOCK TABLES `Supplier_Company` WRITE;
/*!40000 ALTER TABLE `Supplier_Company` DISABLE KEYS */;
INSERT INTO `Supplier_Company` VALUES ('sca2b1','a2b','$argon2id$v=19$m=65536,t=3,p=4$Favt62hF6yvhlu5oWMPBKw$UbWeXtr2m2UWd5bP5mx3npm+p+4Ddfej6XyQHXRy6oQ'),('scpes1','pes','$argon2id$v=19$m=65536,t=3,p=4$VjkVM9U6anUzBFqeRgx1cQ$EeBAAWLvtnKZvmYMu1x3MXHKLByx3LaDc+SAlLAGMgQ');
/*!40000 ALTER TABLE `Supplier_Company` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-08 21:21:35
