-- MySQL dump 10.13  Distrib 8.0.40, for macos14 (arm64)
--
-- Host: localhost    Database: fastapi-vue3-antd-zayum-admin-1.2
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `sys_admin`
--

DROP TABLE IF EXISTS `sys_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL DEFAULT '1',
  `username` varchar(20) NOT NULL,
  `nickname` varchar(50) NOT NULL,
  `password` varchar(128) DEFAULT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(11) NOT NULL,
  `login_failure` int NOT NULL DEFAULT '0',
  `login_at` datetime DEFAULT NULL,
  `login_ip` varchar(50) DEFAULT NULL,
  `token` varchar(512) DEFAULT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin`
--

LOCK TABLES `sys_admin` WRITE;
/*!40000 ALTER TABLE `sys_admin` DISABLE KEYS */;
INSERT INTO `sys_admin` VALUES (1,1,'admin','SupperAdmin','$2b$12$8qJ15oSRtULhh8A/EctDU.MzQm.vyoZRpohknvZqCY5Yr8N9crF4K','/uploads/avatar/avatar_1_c7b7e5.png','13800000000@qq.com','13800000000',0,'2025-11-24 00:24:46','127.0.0.1','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0NTQ4Njg1fQ.ecw6ZOPvPYmXQDs7YhGYiLijWd9z40lrgktORS-T22w','normal','2025-06-26 02:59:10','2025-11-24 00:24:46');
/*!40000 ALTER TABLE `sys_admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_admin_group`
--

DROP TABLE IF EXISTS `sys_admin_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pid` int NOT NULL DEFAULT '0',
  `name` varchar(100) NOT NULL,
  `rules` json NOT NULL,
  `access` json NOT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin_group`
--

LOCK TABLES `sys_admin_group` WRITE;
/*!40000 ALTER TABLE `sys_admin_group` DISABLE KEYS */;
INSERT INTO `sys_admin_group` VALUES (1,0,'super','[\"all\"]','[\"all\"]','normal','2024-04-05 12:15:11','2025-03-04 15:54:49');
/*!40000 ALTER TABLE `sys_admin_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_admin_log`
--

DROP TABLE IF EXISTS `sys_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int NOT NULL,
  `username` varchar(30) NOT NULL,
  `url` varchar(1500) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `content` text NOT NULL,
  `ip` varchar(50) NOT NULL,
  `useragent` text,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_sys_admin_log_created_at` (`created_at`),
  KEY `idx_sys_admin_log_title` (`title`),
  KEY `idx_sys_admin_log_created_date` ((cast(`created_at` as date)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin_log`
--

LOCK TABLES `sys_admin_log` WRITE;
/*!40000 ALTER TABLE `sys_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_admin_rule`
--

DROP TABLE IF EXISTS `sys_admin_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin_rule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rule_type` enum('menu','action') NOT NULL DEFAULT 'menu',
  `parent_id` int DEFAULT NULL,
  `name` varchar(150) NOT NULL,
  `path` varchar(50) NOT NULL,
  `component` varchar(200) DEFAULT NULL,
  `redirect` varchar(100) DEFAULT NULL,
  `meta` json DEFAULT NULL,
  `permission` json DEFAULT NULL,
  `menu_display_type` enum('ajax','addtabs','blank','dialog') DEFAULT 'addtabs',
  `model_name` varchar(80) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `weigh` int NOT NULL DEFAULT '0',
  `status` enum('normal','hidden','deleted') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin_rule`
--

LOCK TABLES `sys_admin_rule` WRITE;
/*!40000 ALTER TABLE `sys_admin_rule` DISABLE KEYS */;
INSERT INTO `sys_admin_rule` VALUES (1,'menu',0,'dashboard','/dashboard/','/_core/dashboard/dashboard','/dashboard','{\"icon\": \"mdi:view-dashboard-outline\", \"title\": \"dashboard.dashboard\"}','{}','addtabs','Dashboard',NULL,1,'normal','2024-01-22 14:32:00','2025-11-11 01:23:42'),(2,'menu',1,'workspace','/dashboard/workspace','/_core/dashboard/workspace/index',NULL,'{\"icon\": \"mdi:view-dashboard-outline\", \"title\": \"dashboard.workspace.workspace\"}','{\"view\": true}','addtabs','Dashboard',NULL,1,'normal','2024-01-22 14:32:00','2025-06-05 00:22:17'),(3,'menu',0,'generals','/generals',NULL,NULL,'{\"icon\": \"mdi:cog-outline\", \"title\": \"general.general\"}','\"{}\"','addtabs','Generals',NULL,2,'normal','2024-01-22 14:32:00','2025-02-28 18:40:34'),(4,'menu',3,'general.profile','/general/profile','/_core/general/profile',NULL,'{\"icon\": \"mdi:account-outline\", \"title\": \"general.profile.profile\"}','{\"edit\": true}','addtabs','GeneralProfile',NULL,11,'normal','2024-01-22 14:32:00','2025-02-28 12:04:00'),(5,'menu',3,'general.category','/general/category','/_core/general/category','','{\"icon\": \"mdi:category-plus-outline\", \"title\": \"general.category.category\", \"menuVisibleWithForbidden\": \"false\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','ajax','GeneralsCategory',NULL,0,'normal','2025-03-04 03:24:40','2025-03-07 11:12:12'),(6,'menu',3,'general.config','/general/config','/_core/general/config',NULL,'{\"icon\": \"mdi:cog-outline\", \"title\": \"general.config.config\"}','{\"add\": true, \"edit\": true, \"delete\": true}','addtabs','GeneralConfig',NULL,8,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31'),(7,'menu',0,'attachments','/attachments',NULL,NULL,'{\"icon\": \"mdi:paperclip\", \"title\": \"attachment.attachment_manage\"}','\"{}\"','blank','Attachment',NULL,9,'normal','2024-01-22 14:32:00','2025-03-06 11:39:00'),(8,'menu',7,'attachment.attachment','/attachment/attachment','/_core/attachment/attachment',NULL,'{\"icon\": \"mdi:file-outline\", \"title\": \"attachment.attachment\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','Attachment',NULL,10,'normal','2024-01-22 14:32:00','2025-03-06 11:39:00'),(9,'menu',0,'plugins','/plugins',NULL,NULL,'{\"icon\": \"mdi:puzzle-outline\", \"title\": \"plugin.plugin\", \"childComponent\": \"/_core/general/profile\"}','\"{}\"','addtabs','Plugin',NULL,3,'normal','2024-01-22 14:32:00','2025-02-28 17:51:12'),(10,'menu',0,'admin','/admin',NULL,NULL,'{\"icon\": \"mdi:shield-account-outline\", \"title\": \"admin.admin.field.admin\"}','\"{}\"','addtabs','Admin',NULL,4,'normal','2024-01-22 14:32:00','2025-06-04 12:15:36'),(11,'menu',10,'admin.admin','/admin/admin','/_core/admin/admin',NULL,'{\"icon\": \"mdi:account-outline\", \"title\": \"admin.admin.admin_manage\"}','{\"add\": true, \"ajax\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','Admin',NULL,20,'normal','2024-01-22 14:32:00','2025-03-06 16:24:24'),(12,'menu',10,'admin.group','/admin/group','/_core/admin/group',NULL,'{\"icon\": \"mdi:account-group-outline\", \"title\": \"admin.group.group\"}','{\"add\": true, \"ajax\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','AdminGroup',NULL,21,'normal','2024-01-22 14:32:00','2025-03-06 13:03:05'),(13,'menu',10,'admin.rule','/admin/rule','/_core/admin/rule',NULL,'{\"icon\": \"mdi:shield-account-outline\", \"title\": \"admin.rule.rule\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','AdminRule',NULL,47,'normal','2024-01-22 14:32:00','2025-03-06 13:03:05'),(14,'menu',10,'admin.log','/admin/log','/_core/admin/log',NULL,'{\"icon\": \"mdi:clipboard-text-outline\", \"title\": \"admin.log.log\"}','{\"view\": true}','addtabs','AdminLog',NULL,50,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31'),(15,'menu',0,'users','/users',NULL,NULL,'{\"icon\": \"mdi:account-multiple-outline\", \"title\": \"user.user\"}','\"{}\"','addtabs','Users',NULL,24,'normal','2024-01-22 14:32:00','2025-02-26 17:47:48'),(16,'menu',15,'user','/user','/_core/user/user',NULL,'{\"icon\": \"mdi:account-outline\", \"title\": \"user.user_manage\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','User',NULL,24,'normal','2024-01-22 14:32:00','2025-03-06 16:19:59'),(17,'menu',15,'user.rule','/user/rule','/_core/user/rule',NULL,'{\"icon\": \"mdi:shield-account-outline\", \"title\": \"user.rule.rule\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserRule',NULL,26,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31'),(18,'menu',15,'user.balance.log','/user/balance/log','/_core/user/balance_log',NULL,'{\"icon\": \"mdi:account-balance-wallet-outline\", \"title\": \"user.balance_log.balance_log\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserBalance',NULL,25,'normal','2024-01-22 14:32:00','2025-03-06 16:27:28'),(19,'menu',15,'user.score.log','/user/score/log','/_core/user/score_log',NULL,'{\"icon\": \"mdi:scoreboard-outline\", \"title\": \"user.score_log.score_log\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserScore',NULL,25,'normal','2024-01-22 14:32:00','2025-03-06 16:28:37'),(20,'menu',15,'user.group','/user/group','/_core/user/group',NULL,'{\"icon\": \"mdi:account-group-outline\", \"title\": \"user.group.group\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserGroup',NULL,0,'normal','2024-09-26 13:01:14','2025-03-04 07:36:31'),(22,'menu',9,'generator','/plugins/generator','/plugins/generator','','{\"icon\": \"mdi:codepen\", \"title\": \"generator.code_generator\", \"menuVisibleWithForbidden\": \"false\"}','{\"view\": true}','ajax','generator',NULL,0,'normal','2025-02-28 10:31:33','2025-03-04 07:36:31'),(24,'menu',7,'attachmentCategory','/attachment/category','/_core/attachment/category','','{\"icon\": \"mdi:attachment\", \"title\": \"attachment.category.category\", \"menuVisibleWithForbidden\": \"false\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','ajax','attachmentCategory',NULL,0,'normal','2025-03-06 03:54:07','2025-03-06 12:56:31'),(25,'menu',9,'plugin','/plugin/plugin','/_core/plugin/plugin','','{\"icon\": \"mdi:shape-rectangle-add\", \"title\": \"plugin.plugin\", \"menuVisibleWithForbidden\": \"false\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','ajax','plugin',NULL,0,'normal','2025-03-09 02:40:04','2025-03-09 11:05:32'),(26,'menu',9,'plugin_store','/plugin/plugin_store','/_core/plugin_store','','{\"icon\": \"mdi:all-inclusive\", \"title\": \"plugin.plugin_store\", \"menuVisibleWithForbidden\": \"false\"}','{\"enable\": true, \"disable\": true, \"install\": true, \"unstall\": true}','ajax','online_plugin',NULL,0,'normal','2025-03-10 07:15:54','2025-03-10 16:07:41'),(27,'menu',1,'analytics','/dashboard/analytics','/_core/dashboard/analytics/index',NULL,'{\"icon\": \"mdi:view-dashboard-outline\", \"title\": \"dashboard.analytics\"}','{\"view\": true}','addtabs','Dashboard',NULL,1,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31');
/*!40000 ALTER TABLE `sys_admin_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_analytics_summary`
--

DROP TABLE IF EXISTS `sys_analytics_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_analytics_summary` (
  `id` varchar(200) NOT NULL,
  `summary_type` enum('daily','monthly','regional') NOT NULL,
  `summary_date` date DEFAULT NULL,
  `summary_year` int DEFAULT NULL,
  `summary_month` int DEFAULT NULL,
  `region_name` varchar(100) DEFAULT NULL,
  `total_users` int DEFAULT '0',
  `new_users` int DEFAULT '0',
  `active_users` int DEFAULT '0',
  `total_logins` int DEFAULT '0',
  `total_visits` int DEFAULT '0',
  `user_group_distribution` json DEFAULT NULL,
  `action_distribution` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_analytics_summary`
--

LOCK TABLES `sys_analytics_summary` WRITE;
/*!40000 ALTER TABLE `sys_analytics_summary` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_analytics_summary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_attachment`
--

DROP TABLE IF EXISTS `sys_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_attachment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cat_id` int DEFAULT '0',
  `admin_id` int NOT NULL,
  `user_id` int NOT NULL,
  `att_type` enum('image','file') DEFAULT 'image',
  `thumb` varchar(255) DEFAULT NULL,
  `path_file` varchar(255) NOT NULL,
  `file_name` varchar(100) DEFAULT NULL,
  `file_size` int NOT NULL,
  `mimetype` varchar(100) DEFAULT NULL,
  `ext_param` varchar(255) DEFAULT NULL,
  `storage` varchar(100) NOT NULL,
  `sha1` varchar(40) DEFAULT NULL,
  `general_attachment_col` varchar(45) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_attachment`
--

LOCK TABLES `sys_attachment` WRITE;
/*!40000 ALTER TABLE `sys_attachment` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_attachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_attachment_category`
--

DROP TABLE IF EXISTS `sys_attachment_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_attachment_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pid` int NOT NULL DEFAULT '0',
  `name` varchar(30) NOT NULL,
  `status` enum('normal','hidden') NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_attachment_category`
--

LOCK TABLES `sys_attachment_category` WRITE;
/*!40000 ALTER TABLE `sys_attachment_category` DISABLE KEYS */;
INSERT INTO `sys_attachment_category` VALUES (1,0,'default','normal','2025-03-06 12:00:02','2025-03-07 09:10:48');
/*!40000 ALTER TABLE `sys_attachment_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_general_category`
--

DROP TABLE IF EXISTS `sys_general_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_general_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pid` int NOT NULL,
  `type` varchar(30) NOT NULL,
  `name` varchar(30) NOT NULL,
  `thumb` varchar(100) DEFAULT NULL,
  `keywords` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `weigh` int NOT NULL,
  `status` enum('normal','hidden') NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_general_category`
--

LOCK TABLES `sys_general_category` WRITE;
/*!40000 ALTER TABLE `sys_general_category` DISABLE KEYS */;
INSERT INTO `sys_general_category` VALUES (1,0,'default','default','','','',0,'normal','2024-05-08 17:19:06','2025-03-07 11:50:19'),(2,0,'blog','news','','','',0,'normal','2025-06-04 17:47:14','2025-06-04 17:47:14');
/*!40000 ALTER TABLE `sys_general_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_general_config`
--

DROP TABLE IF EXISTS `sys_general_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_general_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `group` varchar(30) NOT NULL,
  `title` varchar(100) NOT NULL,
  `tip` varchar(100) DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `visible` varchar(255) DEFAULT NULL,
  `value` text,
  `content` text,
  `rule` varchar(100) DEFAULT NULL,
  `extend` varchar(255) DEFAULT NULL,
  `setting` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_general_config`
--

LOCK TABLES `sys_general_config` WRITE;
/*!40000 ALTER TABLE `sys_general_config` DISABLE KEYS */;
INSERT INTO `sys_general_config` VALUES (1,'name','basic','Site name','Please Input  Site name','string','','栈鱼后台管理系统Pro 1.0','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(2,'copyright','basic','Copyright','Please Input  Copyright','string','','Copyright © 2024 <a href=\"https://zayum.com\" class=\"text-subtitle-2\">栈鱼后台管理系统 1.0</a>. All rights reserved.','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(3,'cdnurl','basic','Cdn url','Please Input  Site name','string','','https://zhanor.com','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(4,'version','basic','Version','Please Input  Version','string','','1.0.1','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(5,'timezone','basic','Timezone','','string','','Asia/Shanghai','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(6,'forbiddenip','basic','Forbidden ip','Please Input  Forbidden ip','text','','12.23.21.1\n1.2.3.6\n34.78.43.1','','','','','2025-04-29 07:12:13','2025-04-29 07:12:13'),(7,'languages','basic','Languages','','array','','{\"frontend\": \"zh-cn\", \"backend\": \"zh-cn\"}','','required','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(8,'fixedpage','basic','Fixed page','Please Input Fixed page','string','','dashboard','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(9,'categorytype','dictionary','Category type','','array','','{\"default\": \"Default\", \"page\": \"Page\", \"article\": \"Article\"}','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(10,'default_category','dictionary','Default Category','','array','','{\"default\": \"Default\"}','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(11,'mail_type','email','Mail type','Please Input Mail type','select','','SMTP','[\"Please Select\",\"SMTP\"]','','','','2024-12-29 01:39:29','2024-12-29 20:59:28'),(12,'mail_smtp_host','email','Mail smtp host','Please Input Mail smtp host','string','','smtp.qq.com','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(13,'mail_smtp_port','email','Mail smtp port','Please Input  Mail smtp port(default25,SSL：465,TLS：587)','string','','465','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(14,'mail_smtp_user','email','Mail smtp user','Please Input Mail smtp user','string','','10000','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(15,'mail_smtp_pass','email','Mail smtp password','Please Input  Mail smtp password','string','','password','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(16,'mail_verify_type','email','Mail vertify type','Please Input Mail vertify type','select','','TLS','[\"None\",\"TLS\",\"SSL\"]','','','','2024-12-29 01:39:29','2024-12-29 20:58:05'),(17,'mail_from','email','Mail from','','string','','10000@qq.com','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(18,'image_category','dictionary','Attachment Image category','','array','','{\"default\": \"Default\", \"blog\": \"Blog\"}','','','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(19,'file_category','dictionary','Attachment File category','','array','','{\"default\": \"Default\", \"product\": \"Product\"}','','','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(20,'video_category','dictionary','Attachment Video category','','array','','{\"default\": \"Default\", \"tutorial\": \"Tutorial\"}','','','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(21,'audio_category','dictionary','Attachment Audio category','','array','','{\"default\": \"Default\", \"music\": \"Music\"}','','','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(22,'document_category','dictionary','Attachment Document category','','array','','{\"default\": \"Default\", \"contract\": \"Contract\"}','','','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(23,'user_page_title','user','User Page Title','User Page Title','string','','User Center','','letters','','','2024-12-29 01:39:29','2024-12-30 12:50:59'),(24,'user_footer','user','User Center Footer','User Center Footer','text','','Copyright © 2024 <a href=\"https://zayum.com\" class=\"link-secondary\">会员中心</a>. All rights reserved.','','required','','','2024-12-29 01:39:29','2024-12-30 12:50:59');
/*!40000 ALTER TABLE `sys_general_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_notification`
--

DROP TABLE IF EXISTS `sys_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_notification` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `receiver_id` int NOT NULL COMMENT '接收者ID',
  `receiver_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'admin' COMMENT '接收者类型: admin/user',
  `sender_id` int DEFAULT NULL COMMENT '发送者ID',
  `sender_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '发送者名称',
  `title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '通知标题',
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '通知内容',
  `type` enum('system','message','comment','reminder','approval','security','update','task') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'system' COMMENT '通知类型',
  `status` enum('unread','read') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'unread' COMMENT '通知状态',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `related_id` int DEFAULT NULL COMMENT '关联数据ID',
  `related_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联数据类型',
  `related_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联URL',
  `priority` int NOT NULL DEFAULT '3' COMMENT '优先级(1-5, 1为最高)',
  `expires_at` datetime DEFAULT NULL COMMENT '过期时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_receiver` (`receiver_id`,`receiver_type`),
  KEY `idx_status` (`status`),
  KEY `idx_type` (`type`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统通知表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_notification`
--

LOCK TABLES `sys_notification` WRITE;
/*!40000 ALTER TABLE `sys_notification` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_plugin`
--

DROP TABLE IF EXISTS `sys_plugin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_plugin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(120) NOT NULL,
  `author` varchar(80) NOT NULL,
  `uuid` varchar(120) NOT NULL,
  `description` varchar(255) NOT NULL,
  `version` varchar(50) NOT NULL,
  `downloads` int NOT NULL,
  `download_url` varchar(255) NOT NULL,
  `md5_hash` varchar(32) NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `paid` smallint NOT NULL,
  `installed` smallint NOT NULL,
  `enabled` smallint NOT NULL,
  `setting_menu` varchar(255) NOT NULL,
  `status` enum('normal','hidden') NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_plugin`
--

LOCK TABLES `sys_plugin` WRITE;
/*!40000 ALTER TABLE `sys_plugin` DISABLE KEYS */;
INSERT INTO `sys_plugin` VALUES (1,'代码生成器','StkFish','generator','generator','1.0.1',12,'2','2',10,0,1,1,'0','normal','2025-03-10 17:09:22','2025-05-09 09:34:40');
/*!40000 ALTER TABLE `sys_plugin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_group_id` int NOT NULL DEFAULT '1',
  `username` varchar(32) NOT NULL,
  `nickname` varchar(50) NOT NULL,
  `password` varchar(120) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(16) NOT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `level` smallint NOT NULL DEFAULT '0',
  `gender` enum('male','female') NOT NULL DEFAULT 'male',
  `birthday` date DEFAULT NULL,
  `bio` varchar(100) DEFAULT 'No  Data',
  `balance` decimal(10,2) DEFAULT '0.00',
  `score` int NOT NULL DEFAULT '0',
  `successions` int NOT NULL DEFAULT '0',
  `max_successions` int NOT NULL DEFAULT '0',
  `prev_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `login_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `login_ip` varchar(50) DEFAULT NULL,
  `login_failure` smallint NOT NULL DEFAULT '0',
  `join_ip` varchar(50) DEFAULT NULL,
  `verification` varchar(255) DEFAULT NULL,
  `token` varchar(250) DEFAULT NULL,
  `status` enum('normal','hidden','delete') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `platform` enum('ios','mac','android','web','pc','other') NOT NULL DEFAULT 'other',
  PRIMARY KEY (`id`),
  KEY `idx_sys_user_created_at` (`created_at`),
  KEY `idx_sys_user_login_time` (`login_time`),
  KEY `idx_sys_user_group_id` (`user_group_id`),
  KEY `idx_sys_user_created_date` ((cast(`created_at` as date))),
  KEY `idx_sys_user_login_date` ((cast(`login_time` as date)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user`
--

LOCK TABLES `sys_user` WRITE;
/*!40000 ALTER TABLE `sys_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_balance_log`
--

DROP TABLE IF EXISTS `sys_user_balance_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_balance_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `balance` decimal(10,0) NOT NULL,
  `before` decimal(10,0) NOT NULL,
  `after` decimal(10,0) NOT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_balance_log`
--

LOCK TABLES `sys_user_balance_log` WRITE;
/*!40000 ALTER TABLE `sys_user_balance_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_user_balance_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_group`
--

DROP TABLE IF EXISTS `sys_user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pid` int NOT NULL DEFAULT '0',
  `name` varchar(100) NOT NULL,
  `rules` json NOT NULL,
  `access` json NOT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_group`
--

LOCK TABLES `sys_user_group` WRITE;
/*!40000 ALTER TABLE `sys_user_group` DISABLE KEYS */;
INSERT INTO `sys_user_group` VALUES (1,0,'super','{\"permissions\": [\"all\"]}','{\"permissions\": [\"all\"]}','normal','2024-04-05 12:15:11','2025-11-19 09:29:53');
/*!40000 ALTER TABLE `sys_user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_rule`
--

DROP TABLE IF EXISTS `sys_user_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_rule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rule_type` enum('menu','action') NOT NULL DEFAULT 'menu',
  `parent_id` int NOT NULL DEFAULT '0',
  `name` varchar(150) NOT NULL,
  `path` varchar(50) NOT NULL,
  `component` varchar(200) DEFAULT NULL,
  `redirect` varchar(100) DEFAULT NULL,
  `meta` json DEFAULT NULL,
  `permission` json DEFAULT NULL,
  `menu_display_type` enum('ajax','addtabs','blank','dialog') DEFAULT 'addtabs',
  `model_name` varchar(80) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `weigh` int NOT NULL DEFAULT '0',
  `status` enum('normal','hidden','deleted') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_rule`
--

LOCK TABLES `sys_user_rule` WRITE;
/*!40000 ALTER TABLE `sys_user_rule` DISABLE KEYS */;
INSERT INTO `sys_user_rule` VALUES (1,'menu',0,'userHome','/home','/user/home','/dashboard','{\"icon\": \"mdi:home\", \"title\": \"home.home\"}','{}','addtabs','Home',NULL,1,'normal','2024-01-22 14:32:00','2025-07-01 09:21:36'),(2,'menu',0,'userProfile','/profile','/user/profile',NULL,'{\"icon\": \"mdi:account\", \"title\": \"profile.profile\"}','{}','addtabs','Profile',NULL,1,'normal','2024-01-22 14:32:00','2025-07-01 09:22:00'),(3,'menu',0,'userSetting','/setting','/user/setting',NULL,'{\"icon\": \"mdi:cog\", \"title\": \"setting.setting\"}','{}','addtabs','Setting',NULL,2,'normal','2024-01-22 14:32:00','2025-07-01 09:21:36');
/*!40000 ALTER TABLE `sys_user_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_score_log`
--

DROP TABLE IF EXISTS `sys_user_score_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_score_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `score` int NOT NULL,
  `before` int NOT NULL,
  `after` int NOT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_score_log`
--

LOCK TABLES `sys_user_score_log` WRITE;
/*!40000 ALTER TABLE `sys_user_score_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_user_score_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-27  9:13:04
