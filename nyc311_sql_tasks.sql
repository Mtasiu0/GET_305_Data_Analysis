-- =============================================================================
-- NYC 311 SQL Sourcing Tasks
-- Author: Data Analyst
-- Description: SQL operations to clean and prepare NYC 311 service request data
-- =============================================================================

-- =============================================================================
-- SECTION 1: RAW DATA IMPORT
-- The raw_311 table contains the original CSV data loaded via Python/pandas.
-- This table should NEVER be modified directly.
-- =============================================================================

-- View raw table structure (for reference only)
-- SELECT * FROM raw_311 LIMIT 5;

-- =============================================================================
-- SECTION 2: DATA VALIDATION CHECKS
-- These queries identify data quality issues before cleaning
-- =============================================================================

-- 2.1 Check for duplicate Unique Key records
-- Rationale: Unique Key should be unique; duplicates indicate data quality issues
SELECT 
    "Unique Key", 
    COUNT(*) as occurrence_count
FROM raw_311
GROUP BY "Unique Key"
HAVING COUNT(*) > 1;

-- 2.2 Check for missing critical fields
-- Rationale: Borough and dates are essential for analysis
SELECT 
    SUM(CASE WHEN Borough IS NULL OR Borough = '' OR Borough = 'Unspecified' THEN 1 ELSE 0 END) as missing_borough,
    SUM(CASE WHEN "Created Date" IS NULL OR "Created Date" = '' THEN 1 ELSE 0 END) as missing_created_date,
    SUM(CASE WHEN Latitude IS NULL OR Latitude = '' THEN 1 ELSE 0 END) as missing_latitude,
    SUM(CASE WHEN Longitude IS NULL OR Longitude = '' THEN 1 ELSE 0 END) as missing_longitude,
    COUNT(*) as total_records
FROM raw_311;

-- 2.3 Check for invalid coordinates
-- Rationale: NYC coordinates should be approximately:
-- Latitude: 40.4 to 40.95, Longitude: -74.3 to -73.6
SELECT COUNT(*) as invalid_coords
FROM raw_311
WHERE (
    CAST(Latitude AS REAL) NOT BETWEEN 40.4 AND 40.95
    OR CAST(Longitude AS REAL) NOT BETWEEN -74.3 AND -73.6
)
AND Latitude IS NOT NULL 
AND Latitude != ''
AND Longitude IS NOT NULL 
AND Longitude != '';

-- 2.4 Check complaint type distribution
-- Rationale: Understanding the variety of complaint types for potential normalization
SELECT 
    "Complaint Type",
    COUNT(*) as complaint_count
FROM raw_311
GROUP BY "Complaint Type"
ORDER BY complaint_count DESC
LIMIT 20;

-- 2.5 Check borough distribution
-- Rationale: Validate borough names and identify inconsistencies
SELECT 
    Borough,
    COUNT(*) as borough_count
FROM raw_311
GROUP BY Borough
ORDER BY borough_count DESC;

-- =============================================================================
-- SECTION 3: CREATE CLEANED ANALYTICAL TABLE
-- This creates the 311_cleaned table with all necessary transformations
-- =============================================================================

DROP TABLE IF EXISTS "311_cleaned";

CREATE TABLE "311_cleaned" AS
SELECT 
    -- Unique identifier - keep first occurrence if duplicates exist
    "Unique Key" AS unique_key,
    
    -- Date fields parsed for analysis
    -- SQLite date format: YYYY-MM-DD HH:MM:SS
    "Created Date" AS created_date_raw,
    "Closed Date" AS closed_date_raw,
    
    -- Parse Created Date to extract components
    -- Format in source: MM/DD/YYYY HH:MM:SS AM/PM
    SUBSTR("Created Date", 7, 4) || '-' || 
    SUBSTR("Created Date", 1, 2) || '-' || 
    SUBSTR("Created Date", 4, 2) AS created_date_parsed,
    
    -- Parse Closed Date similarly
    CASE 
        WHEN "Closed Date" IS NOT NULL AND "Closed Date" != '' 
        THEN SUBSTR("Closed Date", 7, 4) || '-' || 
             SUBSTR("Closed Date", 1, 2) || '-' || 
             SUBSTR("Closed Date", 4, 2)
        ELSE NULL 
    END AS closed_date_parsed,
    
    -- Agency information
    Agency AS agency,
    "Agency Name" AS agency_name,
    
    -- Complaint classification
    "Complaint Type" AS complaint_type,
    
    -- Simplified complaint category (group less common types as 'Other')
    -- Top categories based on typical NYC 311 data
    CASE 
        WHEN "Complaint Type" IN ('HEAT/HOT WATER', 'Noise - Residential', 'Noise - Street/Sidewalk',
                                   'Blocked Driveway', 'Illegal Parking', 'Street Condition',
                                   'Street Light Condition', 'UNSANITARY CONDITION', 
                                   'Water System', 'PLUMBING', 'PAINT/PLASTER', 
                                   'Noise - Commercial', 'Noise', 'Rodent', 
                                   'Sewer', 'Dirty Conditions')
        THEN "Complaint Type"
        ELSE 'Other'
    END AS complaint_category,
    
    Descriptor AS descriptor,
    "Location Type" AS location_type,
    
    -- Geographic information
    "Incident Zip" AS incident_zip,
    
    -- Normalize borough names (handle inconsistencies)
    CASE 
        WHEN UPPER(Borough) = 'BRONX' OR UPPER(Borough) = 'THE BRONX' THEN 'BRONX'
        WHEN UPPER(Borough) = 'BROOKLYN' OR UPPER(Borough) = 'KINGS' THEN 'BROOKLYN'
        WHEN UPPER(Borough) = 'MANHATTAN' OR UPPER(Borough) = 'NEW YORK' THEN 'MANHATTAN'
        WHEN UPPER(Borough) = 'QUEENS' THEN 'QUEENS'
        WHEN UPPER(Borough) = 'STATEN ISLAND' OR UPPER(Borough) = 'RICHMOND' THEN 'STATEN ISLAND'
        WHEN Borough IS NULL OR Borough = '' OR UPPER(Borough) = 'UNSPECIFIED' THEN NULL
        ELSE UPPER(Borough)
    END AS borough,
    
    -- Coordinates - cast to real and validate
    CASE 
        WHEN Latitude IS NOT NULL AND Latitude != '' 
             AND CAST(Latitude AS REAL) BETWEEN 40.4 AND 40.95
        THEN CAST(Latitude AS REAL)
        ELSE NULL 
    END AS latitude,
    
    CASE 
        WHEN Longitude IS NOT NULL AND Longitude != ''
             AND CAST(Longitude AS REAL) BETWEEN -74.3 AND -73.6
        THEN CAST(Longitude AS REAL)
        ELSE NULL 
    END AS longitude,
    
    -- Status
    Status AS status,
    
    -- Resolution information
    "Resolution Description" AS resolution_description,
    "Resolution Action Updated Date" AS resolution_action_date,
    
    -- Community board
    "Community Board" AS community_board,
    
    -- Address components
    "Incident Address" AS incident_address,
    City AS city,
    
    -- Validity flags for filtering
    CASE 
        WHEN Borough IS NULL OR Borough = '' OR UPPER(Borough) = 'UNSPECIFIED' THEN 0
        ELSE 1 
    END AS has_valid_borough,
    
    CASE 
        WHEN Latitude IS NOT NULL AND Latitude != '' 
             AND Longitude IS NOT NULL AND Longitude != ''
             AND CAST(Latitude AS REAL) BETWEEN 40.4 AND 40.95
             AND CAST(Longitude AS REAL) BETWEEN -74.3 AND -73.6
        THEN 1
        ELSE 0 
    END AS has_valid_coordinates,
    
    CASE 
        WHEN "Created Date" IS NOT NULL AND "Created Date" != '' 
        THEN 1
        ELSE 0 
    END AS has_valid_created_date,
    
    CASE 
        WHEN "Closed Date" IS NOT NULL AND "Closed Date" != '' 
        THEN 1
        ELSE 0 
    END AS has_closed_date

FROM raw_311

-- Remove exact duplicates based on Unique Key (keep first occurrence)
WHERE "Unique Key" IN (
    SELECT MIN("Unique Key") 
    FROM raw_311 
    GROUP BY "Unique Key"
)

-- Filter out records with nonsensical dates (year before 2010 or after current year)
AND (
    "Created Date" IS NULL 
    OR "Created Date" = ''
    OR CAST(SUBSTR("Created Date", 7, 4) AS INTEGER) BETWEEN 2010 AND 2026
);

-- =============================================================================
-- SECTION 4: POST-CREATION VALIDATION
-- Verify the cleaned table was created correctly
-- =============================================================================

-- 4.1 Count records in cleaned table vs raw
SELECT 
    (SELECT COUNT(*) FROM raw_311) AS raw_count,
    (SELECT COUNT(*) FROM "311_cleaned") AS cleaned_count,
    (SELECT COUNT(*) FROM raw_311) - (SELECT COUNT(*) FROM "311_cleaned") AS records_removed;

-- 4.2 Verify no duplicates in cleaned table
SELECT 
    unique_key, 
    COUNT(*) as cnt
FROM "311_cleaned"
GROUP BY unique_key
HAVING COUNT(*) > 1;

-- 4.3 Summary statistics for cleaned data
SELECT
    COUNT(*) AS total_records,
    SUM(has_valid_borough) AS records_with_borough,
    SUM(has_valid_coordinates) AS records_with_coords,
    SUM(has_closed_date) AS records_with_closed_date,
    COUNT(DISTINCT borough) AS unique_boroughs,
    COUNT(DISTINCT complaint_type) AS unique_complaint_types
FROM "311_cleaned";

-- 4.4 Borough distribution in cleaned data
SELECT 
    borough,
    COUNT(*) as record_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM "311_cleaned"), 2) AS percentage
FROM "311_cleaned"
WHERE borough IS NOT NULL
GROUP BY borough
ORDER BY record_count DESC;

-- 4.5 Top complaint types in cleaned data
SELECT 
    complaint_type,
    COUNT(*) as record_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM "311_cleaned"), 2) AS percentage
FROM "311_cleaned"
GROUP BY complaint_type
ORDER BY record_count DESC
LIMIT 15;

-- =============================================================================
-- SECTION 5: CREATE INDEXES FOR PERFORMANCE
-- Optimize query performance for analytical workloads
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_cleaned_borough ON "311_cleaned"(borough);
CREATE INDEX IF NOT EXISTS idx_cleaned_complaint_type ON "311_cleaned"(complaint_type);
CREATE INDEX IF NOT EXISTS idx_cleaned_created_date ON "311_cleaned"(created_date_parsed);
CREATE INDEX IF NOT EXISTS idx_cleaned_unique_key ON "311_cleaned"(unique_key);

-- =============================================================================
-- END OF SQL SOURCING TASKS
-- =============================================================================
