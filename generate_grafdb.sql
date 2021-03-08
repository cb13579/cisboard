-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema grafdb
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `grafdb` ;

-- -----------------------------------------------------
-- Schema grafdb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `grafdb` DEFAULT CHARACTER SET utf8 ;
USE `grafdb` ;

-- -----------------------------------------------------
-- Table `grafdb`.`t_systemtype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `grafdb`.`t_systemtype` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `grafdb`.`t_benchmark`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `grafdb`.`t_benchmark` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `level` VARCHAR(200) NOT NULL,
  `t_systemtype_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_t_benchmark_t_systemtype1_idx` (`t_systemtype_id` ASC),
  CONSTRAINT `fk_t_benchmark_t_systemtype1`
    FOREIGN KEY (`t_systemtype_id`)
    REFERENCES `grafdb`.`t_systemtype` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `grafdb`.`t_testname`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `grafdb`.`t_testname` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `position_in_benchmark` VARCHAR(20) NOT NULL,
  `name` VARCHAR(250) NOT NULL,
  `layer` INT NOT NULL,
  `layerposition` INT NULL,
  `headline` VARCHAR(200) NULL,
  `t_benchmark_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_t_testname_t_benchmark1_idx` (`t_benchmark_id` ASC),
  CONSTRAINT `fk_t_testname_t_benchmark1`
    FOREIGN KEY (`t_benchmark_id`)
    REFERENCES `grafdb`.`t_benchmark` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `grafdb`.`t_benchresult`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `grafdb`.`t_benchresult` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `score` DOUBLE NULL,
  `executed` TIMESTAMP NULL,
  `target` VARCHAR(200) NULL,
  `t_benchmark_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_t_benchresult_t_benchmark_idx` (`t_benchmark_id` ASC),
  CONSTRAINT `fk_t_benchresult_t_benchmark`
    FOREIGN KEY (`t_benchmark_id`)
    REFERENCES `grafdb`.`t_benchmark` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `grafdb`.`t_testresult`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `grafdb`.`t_testresult` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `score` DOUBLE NOT NULL,
  `t_benchresult_id` INT NOT NULL,
  `t_testname_id` INT NOT NULL,
  `percent` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_t_testresult_t_benchresult1_idx` (`t_benchresult_id` ASC),
  INDEX `fk_t_testresult_t_testname1_idx` (`t_testname_id` ASC),
  CONSTRAINT `fk_t_testresult_t_benchresult1`
    FOREIGN KEY (`t_benchresult_id`)
    REFERENCES `grafdb`.`t_benchresult` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_t_testresult_t_testname1`
    FOREIGN KEY (`t_testname_id`)
    REFERENCES `grafdb`.`t_testname` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
