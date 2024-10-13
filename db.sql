-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: localhost    Database: dbms_project_testing1
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
INSERT INTO `Admin` VALUES ('admf31','Mohammed','Furqaan','Patel','$argon2id$v=19$m=65536,t=3,p=4$cppClCyw38RoMUIar2T7Fw$o1wXr9mc/ZwX7xzAL7xvr+rimkhkPbdX3loMDhtDbiI'),('admh13','Manu','Narayan','Hegde','$argon2id$v=19$m=65536,t=3,p=4$exaj8cuUaDAc7DpNr2XnLw$ToZXUg4cDU46D9aQn9eu7HJ4VFL1g4PrjOMzf1sV0s8');
/*!40000 ALTER TABLE `Admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Company_Inventory`
--

DROP TABLE IF EXISTS `Company_Inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Company_Inventory` (
  `Inventory_id` int NOT NULL AUTO_INCREMENT,
  `Construction_Company_name` varchar(100) NOT NULL,
  `Product_name` varchar(100) NOT NULL,
  `Quantity` int NOT NULL,
  PRIMARY KEY (`Inventory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Company_Inventory`
--

LOCK TABLES `Company_Inventory` WRITE;
/*!40000 ALTER TABLE `Company_Inventory` DISABLE KEYS */;
INSERT INTO `Company_Inventory` VALUES (2,'Prestige','CEMENT',50),(3,'Prestige','IRON',50),(4,'Ashed','IRON',50);
/*!40000 ALTER TABLE `Company_Inventory` ENABLE KEYS */;
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
  `Cash_Balance` decimal(20,2) DEFAULT '10000000.00',
  `Admin_id` varchar(50) DEFAULT NULL,
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
INSERT INTO `Construction_Company` VALUES ('ccah1','Ashed',9991000.00,'admh13'),('ccpg1','Prestige',8973751.00,'admf31');
/*!40000 ALTER TABLE `Construction_Company` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Order_info`
--

DROP TABLE IF EXISTS `Order_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Order_info` (
  `Order_id` varchar(50) NOT NULL,
  `Product_id` varchar(50) DEFAULT NULL,
  `Construction_Company_Id` varchar(50) DEFAULT NULL,
  `Supplier_Company_Id` varchar(50) DEFAULT NULL,
  `Shipment_Company_Id` varchar(50) DEFAULT NULL,
  `Quantity` int NOT NULL,
  `Cost` decimal(10,2) DEFAULT NULL,
  `Status` enum('Pending','Accepted','Rejected') DEFAULT 'Pending',
  PRIMARY KEY (`Order_id`),
  KEY `Product_id` (`Product_id`),
  KEY `Construction_Company_Id` (`Construction_Company_Id`),
  KEY `Supplier_Company_Id` (`Supplier_Company_Id`),
  KEY `Shipment_Company_Id` (`Shipment_Company_Id`),
  CONSTRAINT `Order_info_ibfk_1` FOREIGN KEY (`Product_id`) REFERENCES `Product_info` (`Product_id`),
  CONSTRAINT `Order_info_ibfk_2` FOREIGN KEY (`Construction_Company_Id`) REFERENCES `Construction_Company` (`Construction_Company_id`),
  CONSTRAINT `Order_info_ibfk_3` FOREIGN KEY (`Supplier_Company_Id`) REFERENCES `Supplier_Company` (`Supplier_Company_id`),
  CONSTRAINT `Order_info_ibfk_4` FOREIGN KEY (`Shipment_Company_Id`) REFERENCES `Shipment_Company` (`Shipment_Company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Order_info`
--

LOCK TABLES `Order_info` WRITE;
/*!40000 ALTER TABLE `Order_info` DISABLE KEYS */;
INSERT INTO `Order_info` VALUES ('OR07e1','cmt1','ccah1','sca2b1',NULL,50,100000.00,'Rejected'),('OR256f','fe35','ccah1','sca2b1','FDX',60,9000.00,'Accepted'),('OR6af6','nl1','ccah1','scpes1',NULL,2,100.00,'Pending'),('OR8708','cmt1','ccpg1','sca2b1','FDX',10,20000.00,'Accepted'),('ORbd1f','fe45','ccpg1','scpes1','DHL',25,2500.00,'Accepted'),('ORc446','cmt2','ccpg1','scpes1','DHL',40,1000000.00,'Accepted'),('ORfc76','fe35','ccpg1','sca2b1','FDX',25,3750.00,'Accepted');
/*!40000 ALTER TABLE `Order_info` ENABLE KEYS */;
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
INSERT INTO `Product_info` VALUES ('cmt1','CEMENT',2000.00,'sca2b1'),('cmt2','CEMENT',25000.00,'scpes1'),('fe35','IRON',150.00,'sca2b1'),('fe45','IRON',100.00,'scpes1'),('nl1','NAIL',50.00,'scpes1');
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
  `Shipment_Company_name` varchar(100) NOT NULL,
  PRIMARY KEY (`Shipment_Company_id`),
  UNIQUE KEY `Shipment_Company_name` (`Shipment_Company_name`)
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
INSERT INTO `Supplier_Company` VALUES ('sca2b1','a2b','$argon2id$v=19$m=65536,t=3,p=4$gF0Ryats9UHatJhUcam6dw$2FsyhNqcUZshKPjRyM6NEFZFeN0HirEyHO3m9CFPqBY'),('scpes1','pes','$argon2id$v=19$m=65536,t=3,p=4$aMmI20T58dPexueJHjJOQw$UnI7jRhuzW+8nf4AUEVuoSiiXXqEww0gICizsAVrtqI');
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

-- Dump completed on 2024-10-13 15:34:35
