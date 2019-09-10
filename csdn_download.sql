/*
Navicat MySQL Data Transfer

Source Server         : 远程
Source Server Version : 50644
Source Host           : 45.248.86.152:3306
Source Database       : csdn_download

Target Server Type    : MYSQL
Target Server Version : 50644
File Encoding         : 65001

Date: 2019-09-10 21:41:43
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for account
-- ----------------------------
DROP TABLE IF EXISTS `account`;
CREATE TABLE `account` (
  `type` varchar(255) NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `user_data_dir` varchar(255) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `today` int(11) NOT NULL,
  `remain` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `update_time` datetime DEFAULT NULL,
  UNIQUE KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for chongzhi
-- ----------------------------
DROP TABLE IF EXISTS `chongzhi`;
CREATE TABLE `chongzhi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `qq` varchar(255) NOT NULL,
  `count` int(11) NOT NULL,
  `time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `qq_chongzhi` (`qq`),
  CONSTRAINT `qq_chongzhi` FOREIGN KEY (`qq`) REFERENCES `user` (`qq`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for direct_return
-- ----------------------------
DROP TABLE IF EXISTS `direct_return`;
CREATE TABLE `direct_return` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for download
-- ----------------------------
DROP TABLE IF EXISTS `download`;
CREATE TABLE `download` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `qq` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `size` varchar(255) DEFAULT NULL,
  `download_path` varchar(255) DEFAULT NULL,
  `download_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `qq` (`qq`),
  CONSTRAINT `qq` FOREIGN KEY (`qq`) REFERENCES `user` (`qq`)
) ENGINE=InnoDB AUTO_INCREMENT=250 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for new_friend
-- ----------------------------
DROP TABLE IF EXISTS `new_friend`;
CREATE TABLE `new_friend` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `qq` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `qqw` (`qq`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(255) NOT NULL AUTO_INCREMENT,
  `qq` varchar(255) NOT NULL,
  `download_count` int(11) NOT NULL,
  `remain` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `qq` (`qq`)
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8;
