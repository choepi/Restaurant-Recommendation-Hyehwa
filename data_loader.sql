

create database project;
use project;
#drop database project;
#SHOW VARIABLES LIKE "secure_file_priv";
select * from category;

SELECT restaurant_id
            FROM restaurant
            WHERE restaurant_id IN (336, 189, 224, 81, 26)
            AND category_id IN (1, 2, 3, 4, 5, 6, 7, 8);

SELECT restaurant_id
            FROM restaurant
            WHERE restaurant_id IN (193, 132, 260, 375, 228)
            AND category_id = (1);
            
select*from category;