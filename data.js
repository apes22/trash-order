const INITIAL_DATA = [
  // ===== BEVERAGE =====
  { id: 1, category: "BEVERAGE", vendor: "Coca-Cola", packSize: "24 12 oz", brand: "Coca-Cola", item: "Coca-Cola (glass)", unit: "each", totalWeightOz: 288, pricePerPkg: 22.42, perLbPint: 4.08, perOzUnit: 0.93, notes: "", par: 0, onHand: 0 },
  { id: 2, category: "BEVERAGE", vendor: "Coca-Cola", packSize: "24 12 oz", brand: "Coca-Cola", item: "Dr. Pepper (glass)", unit: "each", totalWeightOz: 288, pricePerPkg: 22.42, perLbPint: 3.80, perOzUnit: 0.93, notes: "", par: 0, onHand: 0 },
  { id: 3, category: "BEVERAGE", vendor: "Coca-Cola", packSize: "24 12 oz", brand: "Coca-Cola", item: "Sprite (glass)", unit: "each", totalWeightOz: 288, pricePerPkg: 22.42, perLbPint: 4.91, perOzUnit: 0.83, notes: "", par: 0, onHand: 0 },
  { id: 4, category: "BEVERAGE", vendor: "Coca-Cola", packSize: "24 12 oz", brand: "Coca-Cola", item: "Barq's Root Beer (glass)", unit: "each", totalWeightOz: 288, pricePerPkg: 22.42, perLbPint: 2.94, perOzUnit: 0.83, notes: "", par: 0, onHand: 0 },
  { id: 5, category: "BEVERAGE", vendor: "Coca-Cola", packSize: "24 12 oz", brand: "Coca-Cola", item: "Fanta (glass, assort. flavors)", unit: "each", totalWeightOz: 288, pricePerPkg: 22.42, perLbPint: 0, perOzUnit: 0.83, notes: "", par: 0, onHand: 0 },
  { id: 6, category: "BEVERAGE", vendor: "Coca-Cola", packSize: "24 20 oz", brand: "Coca-Cola", item: "Dasani Water", unit: "each", totalWeightOz: 480, pricePerPkg: 22.87, perLbPint: 0, perOzUnit: 0.85, notes: "", par: 0, onHand: 0 },

  // ===== FOOD =====
  // Candy
  { id: 7, category: "FOOD", vendor: "SGC", packSize: "1 20 lb", brand: "Churn", item: "candy, Andes mints topping", unit: "ozs", totalWeightOz: 320, pricePerPkg: 81.84, perLbPint: 4.08, perOzUnit: 0.26, notes: "", par: 0, onHand: 0 },
  { id: 8, category: "FOOD", vendor: "SGC", packSize: "1 25#", brand: "Ferraro", item: "candy, Butterfinger pieces", unit: "ozs", totalWeightOz: 400, pricePerPkg: 84.99, perLbPint: 3.80, perOzUnit: 0.21, notes: "S/O", par: 0, onHand: 0 },
  { id: 9, category: "FOOD", vendor: "Walmart", packSize: "1 12 oz", brand: "Great Value", item: "candy, chocolate chips", unit: "ozs", totalWeightOz: 12, pricePerPkg: 3.68, perLbPint: 2.94, perOzUnit: 0.31, notes: "", par: 0, onHand: 0 },
  { id: 10, category: "FOOD", vendor: "Webstaurant", packSize: "4 4.5#", brand: "Albanese", item: "candy, gummy worms mini", unit: "ozs", totalWeightOz: 288, pricePerPkg: 64.99, perLbPint: 3.75, perOzUnit: 0.23, notes: "", par: 0, onHand: 0 },
  { id: 11, category: "FOOD", vendor: "SGC", packSize: "2 5 lb", brand: "TRTopper", item: "candy, gummy bears mini", unit: "ozs", totalWeightOz: 160, pricePerPkg: 70.29, perLbPint: 7.03, perOzUnit: 0.44, notes: "", par: 0, onHand: 0 },
  { id: 12, category: "FOOD", vendor: "SGC", packSize: "4 2.5 lb", brand: "TRTopper", item: "candy, Heath bits w choc", unit: "ozs", totalWeightOz: 160, pricePerPkg: 74.33, perLbPint: 7.43, perOzUnit: 0.46, notes: "", par: 0, onHand: 0 },
  { id: 13, category: "FOOD", vendor: "SGC", packSize: "2 4 lb", brand: "TRTopper", item: "candy, Kit Kat bits", unit: "ozs", totalWeightOz: 128, pricePerPkg: 44.29, perLbPint: 5.54, perOzUnit: 0.35, notes: "", par: 0, onHand: 0 },
  { id: 14, category: "FOOD", vendor: "SGC", packSize: "2 4 lb", brand: "TRTopper", item: "candy, M & Ms chopped", unit: "ozs", totalWeightOz: 128, pricePerPkg: 64.49, perLbPint: 5.45, perOzUnit: 0.34, notes: "", par: 0, onHand: 0 },
  { id: 15, category: "FOOD", vendor: "Webstaurant", packSize: "1 10 lb", brand: "Nestle", item: "candy, Nerds rainbow", unit: "ozs", totalWeightOz: 160, pricePerPkg: 68.67, perLbPint: 6.86, perOzUnit: 0.43, notes: "", par: 0, onHand: 0 },
  { id: 16, category: "FOOD", vendor: "Webstaurant", packSize: "1 10 lb", brand: "TRTopper", item: "candy, Reese's peanut butter cups", unit: "ozs", totalWeightOz: 160, pricePerPkg: 98.87, perLbPint: 4.58, perOzUnit: 0.29, notes: "", par: 0, onHand: 0 },
  { id: 17, category: "FOOD", vendor: "SGC", packSize: "2 5 lb", brand: "TRTopper", item: "candy, Reese's Pieces mini", unit: "ozs", totalWeightOz: 160, pricePerPkg: 114.42, perLbPint: 2.89, perOzUnit: 0.58, notes: "", par: 0, onHand: 0 },

  // Cereal
  { id: 18, category: "FOOD", vendor: "Walmart", packSize: "1 40 oz", brand: "GM", item: "cereal, Cap'n Crunch Berries", unit: "ozs", totalWeightOz: 40, pricePerPkg: 6.77, perLbPint: 2.89, perOzUnit: 0.17, notes: "", par: 0, onHand: 0 },
  { id: 19, category: "FOOD", vendor: "Walmart", packSize: "1 32 oz", brand: "Quaker", item: "cereal, Cinnamon Toast Crunch", unit: "ozs", totalWeightOz: 32, pricePerPkg: 33.48, perLbPint: 3.39, perOzUnit: 0.21, notes: "", par: 0, onHand: 0 },
  { id: 20, category: "FOOD", vendor: "Walmart", packSize: "1 25 lb", brand: "MOM", item: "cereal, Fruity Dyno Bites", unit: "ozs", totalWeightOz: 184, pricePerPkg: 7.02, perLbPint: 2.81, perOzUnit: 0.18, notes: "", par: 0, onHand: 0 },
  { id: 21, category: "FOOD", vendor: "SGC", packSize: "4 4.48 oz", brand: "GM", item: "cereal, Golden Grahams", unit: "ozs", totalWeightOz: 35, pricePerPkg: 33.48, perLbPint: 3.21, perOzUnit: 0.20, notes: "", par: 0, onHand: 0 },

  // Spices / Coffee
  { id: 22, category: "FOOD", vendor: "SGC", packSize: "1 18 oz", brand: "Spice Classics", item: "cinnamon, ground", unit: "ozs", totalWeightOz: 18, pricePerPkg: 7.98, perLbPint: 7.09, perOzUnit: 0.44, notes: "", par: 0, onHand: 0 },
  { id: 23, category: "FOOD", vendor: "Sam's Club", packSize: "2 10.5 oz", brand: "State Fair", item: "coffee, instant", unit: "ozs", totalWeightOz: 21, pricePerPkg: 19.83, perLbPint: 0, perOzUnit: 0.90, notes: "", par: 0, onHand: 0 },

  // Cones
  { id: 24, category: "FOOD", vendor: "Webstaurant", packSize: "12 18 ct", brand: "JOY", item: "cones, waffle lg prepacketed", unit: "each", totalWeightOz: 216, pricePerPkg: 69.18, perLbPint: 0, perOzUnit: 0.35, notes: "", par: 0, onHand: 0 },
  { id: 25, category: "FOOD", vendor: "SGC", packSize: "12 18 ct", brand: "JOY", item: "cones, sugar mini", unit: "each", totalWeightOz: 1000, pricePerPkg: 102.99, perLbPint: 4.90, perOzUnit: 0.10, notes: "", par: 0, onHand: 0 },

  // Cookies
  { id: 26, category: "FOOD", vendor: "Webstaurant", packSize: "1 1000 ct", brand: "TRTopper", item: "cookies, brownie bites", unit: "ozs", totalWeightOz: 100, pricePerPkg: 76.49, perLbPint: 4.10, perOzUnit: 0.35, notes: "", par: 0, onHand: 0 },
  { id: 27, category: "FOOD", vendor: "SGC", packSize: "1 10 lb", brand: "TRTopper", item: "cookies, cheesecake bites", unit: "ozs", totalWeightOz: 160, pricePerPkg: 48.83, perLbPint: 8.10, perOzUnit: 0.31, notes: "", par: 0, onHand: 0 },
  { id: 28, category: "FOOD", vendor: "SGC", packSize: "1 10 lb", brand: "Rhino", item: "cookies, Biscoff crumbs", unit: "ozs", totalWeightOz: 320, pricePerPkg: 61.02, perLbPint: 2.59, perOzUnit: 0.38, notes: "", par: 0, onHand: 0 },
  { id: 29, category: "FOOD", vendor: "SGC", packSize: "1 20 lbs", brand: "Lotus", item: "cookies, cookie dough", unit: "ozs", totalWeightOz: 264, pricePerPkg: 51.85, perLbPint: 4.68, perOzUnit: 0.16, notes: "", par: 0, onHand: 0 },
  { id: 30, category: "FOOD", vendor: "Walmart", packSize: "1 16.53 lb", brand: "Mother's", item: "cookies, circus animals", unit: "ozs", totalWeightOz: 9, pricePerPkg: 76.99, perLbPint: 4.08, perOzUnit: 0.29, notes: "", par: 0, onHand: 0 },
  { id: 31, category: "FOOD", vendor: "Walmart", packSize: "1 9 oz", brand: "Nabisco", item: "cookies, Nutter Butters", unit: "ozs", totalWeightOz: 18, pricePerPkg: 3.52, perLbPint: 4.89, perOzUnit: 0.39, notes: "", par: 0, onHand: 0 },
  { id: 32, category: "FOOD", vendor: "Walmart", packSize: "1 16 oz", brand: "Nabisco", item: "cookies, Oreos sm crumbs", unit: "ozs", totalWeightOz: 384, pricePerPkg: 4.89, perLbPint: 4.26, perOzUnit: 0.30, notes: "", par: 0, onHand: 0 },
  { id: 33, category: "FOOD", vendor: "Webstaurant", packSize: "24 1 lb", brand: "Nabisco", item: "cookies, pie chips", unit: "ozs", totalWeightOz: 160, pricePerPkg: 87.73, perLbPint: 4.07, perOzUnit: 0.25, notes: "", par: 0, onHand: 0 },

  // Crackers / Donuts
  { id: 34, category: "FOOD", vendor: "SGC", packSize: "1 10 lb", brand: "TRTopper", item: "crackers, Ritz", unit: "ozs", totalWeightOz: 76, pricePerPkg: 134.00, perLbPint: 13.60, perOzUnit: 0.85, notes: "", par: 0, onHand: 0 },
  { id: 35, category: "FOOD", vendor: "Walmart", packSize: "1 10 lb", brand: "State Fair", item: "donuts, mini plain", unit: "ozs", totalWeightOz: 160, pricePerPkg: 25.24, perLbPint: 5.52, perOzUnit: 0.35, notes: "", par: 0, onHand: 0 },

  // Fruit
  { id: 36, category: "FOOD", vendor: "SGC", packSize: "20 3.8 oz", brand: "Dole", item: "fruit, bananas iqf", unit: "ozs", totalWeightOz: 40, pricePerPkg: 20.13, perLbPint: 3.58, perOzUnit: 0.22, notes: "", par: 0, onHand: 0 },
  { id: 37, category: "FOOD", vendor: "Walmart", packSize: "1 40 oz", brand: "Great Value", item: "fruit, dark sweet cherries w stem", unit: "ozs", totalWeightOz: 160, pricePerPkg: 8.98, perLbPint: 2.02, perOzUnit: 0.13, notes: "", par: 0, onHand: 0 },
  { id: 38, category: "FOOD", vendor: "SGC", packSize: "2 58 bag", brand: "State Fair", item: "fruit, maraschino cherries w stem jar", unit: "jar", totalWeightOz: 384, pricePerPkg: 93.38, perLbPint: 15.56, perOzUnit: 0.24, notes: "$15.56", par: 0, onHand: 0 },

  // Fruit (page 2)
  { id: 39, category: "FOOD", vendor: "SGC", packSize: "2 5 lb", brand: "Commodity", item: "fruit, peaches iqf", unit: "ozs", totalWeightOz: 160, pricePerPkg: 29.37, perLbPint: 2.94, perOzUnit: 0.18, notes: "", par: 0, onHand: 0 },
  { id: 40, category: "FOOD", vendor: "SGC", packSize: "1 5 lb", brand: "Commodity", item: "fruit, raspberries sliced iqf", unit: "ozs", totalWeightOz: 320, pricePerPkg: 19.78, perLbPint: 0.99, perOzUnit: 0.06, notes: "", par: 0, onHand: 0 },
  { id: 41, category: "FOOD", vendor: "SGC", packSize: "1 2.5 lb", brand: "Commodity", item: "fruit, strawberries sliced iqf", unit: "ozs", totalWeightOz: 160, pricePerPkg: 28.21, perLbPint: 2.82, perOzUnit: 0.18, notes: "", par: 0, onHand: 0 },

  // Ice Cream
  { id: 42, category: "FOOD", vendor: "SGC", packSize: "1 2.5 gal", brand: "ICF", item: "ice cream, chocolate", unit: "tub", totalWeightOz: 320, pricePerPkg: 32.50, perLbPint: 10.83, perOzUnit: 0.10, notes: "", par: 0, onHand: 0 },
  { id: 43, category: "FOOD", vendor: "SGC", packSize: "1 2.5 gal", brand: "ICF", item: "ice cream, coconut dairy free", unit: "tub", totalWeightOz: 320, pricePerPkg: 68.01, perLbPint: 22.67, perOzUnit: 0.21, notes: "", par: 0, onHand: 0 },
  { id: 44, category: "FOOD", vendor: "SGC", packSize: "1 2.5 gal", brand: "ICF", item: "ice cream, vanilla", unit: "tub", totalWeightOz: 320, pricePerPkg: 33.00, perLbPint: 11.00, perOzUnit: 0.10, notes: "", par: 0, onHand: 0 },
  { id: 45, category: "FOOD", vendor: "SGC", packSize: "1 1 gal", brand: "Hiland", item: "ice cream, shake mix 5%", unit: "gal", totalWeightOz: 128, pricePerPkg: 46.53, perLbPint: 12.13, perOzUnit: 0.09, notes: "$12.13 ea", par: 0, onHand: 0 },
  { id: 46, category: "FOOD", vendor: "SGC", packSize: "12 12 oz pint", brand: "ICF", item: "ice cream, pint Blue Your Mind", unit: "pint", totalWeightOz: 144, pricePerPkg: 52.69, perLbPint: 4.39, perOzUnit: 0.37, notes: "", par: 0, onHand: 0 },
  { id: 47, category: "FOOD", vendor: "SGC", packSize: "12 12 oz pint", brand: "ICF", item: "ice cream, pint Bustin' Berries", unit: "pint", totalWeightOz: 144, pricePerPkg: 52.69, perLbPint: 4.39, perOzUnit: 0.37, notes: "", par: 0, onHand: 0 },
  { id: 48, category: "FOOD", vendor: "SGC", packSize: "12 12 oz pint", brand: "ICF", item: "ice cream, pint Dirty Cheesecake", unit: "pint", totalWeightOz: 144, pricePerPkg: 52.69, perLbPint: 4.39, perOzUnit: 0.37, notes: "", par: 0, onHand: 0 },

  // Dairy / Powders
  { id: 49, category: "FOOD", vendor: "Walmart", packSize: "1 13 oz", brand: "Silk", item: "malted milk powder", unit: "ozs", totalWeightOz: 13, pricePerPkg: 5.34, perLbPint: 1.04, perOzUnit: 0.41, notes: "", par: 0, onHand: 0 },
  { id: 50, category: "FOOD", vendor: "Walmart", packSize: "1 1/2 gal", brand: "Great Value", item: "milk, coconut", unit: "ozs", totalWeightOz: 64, pricePerPkg: 4.17, perLbPint: 0.57, perOzUnit: 0.07, notes: "", par: 0, onHand: 0 },

  // Nuts
  { id: 51, category: "FOOD", vendor: "SGC", packSize: "1 16 oz", brand: "Azar", item: "nuts, almonds sliced", unit: "ozs", totalWeightOz: 18, pricePerPkg: 8.48, perLbPint: 8.48, perOzUnit: 0.53, notes: "", par: 0, onHand: 0 },
  { id: 52, category: "FOOD", vendor: "SGC", packSize: "6 17.5#", brand: "Great Value", item: "nuts, coconut sweetened shred", unit: "ozs", totalWeightOz: 14, pricePerPkg: 143.76, perLbPint: 13.88, perOzUnit: 0.87, notes: "", par: 0, onHand: 0 },
  { id: 53, category: "FOOD", vendor: "SGC", packSize: "1 14 oz", brand: "Great Value", item: "nuts, peanuts granulated", unit: "ozs", totalWeightOz: 50, pricePerPkg: 3.22, perLbPint: 3.68, perOzUnit: 0.23, notes: "", par: 0, onHand: 0 },
  { id: 54, category: "FOOD", vendor: "Sam's Club", packSize: "3 2#", brand: "Member's Mark", item: "nuts, pecan halves", unit: "ozs", totalWeightOz: 490, pricePerPkg: 27.54, perLbPint: 5.59, perOzUnit: 0.41, notes: "", par: 0, onHand: 0 },

  // Pretzels / PB
  { id: 55, category: "FOOD", vendor: "Walmart", packSize: "1 32 oz", brand: "Great Value", item: "pretzels, mini twists", unit: "ozs", totalWeightOz: 16, pricePerPkg: 177.12, perLbPint: 6.49, perOzUnit: 0.41, notes: "", par: 0, onHand: 0 },
  { id: 56, category: "FOOD", vendor: "Walmart", packSize: "1 16 oz", brand: "JIF", item: "peanut butter, no added sugar", unit: "ozs", totalWeightOz: 32, pricePerPkg: 2.44, perLbPint: 6.44, perOzUnit: 0.15, notes: "", par: 0, onHand: 0 },

  // Sprinkles
  { id: 57, category: "FOOD", vendor: "Webstaurant", packSize: "1 10 lbs", brand: "Regal", item: "sprinkles, rainbow bulk", unit: "ozs", totalWeightOz: 180, pricePerPkg: 33.5, perLbPint: 3.14, perOzUnit: 0.20, notes: "", par: 0, onHand: 0 },
  { id: 58, category: "FOOD", vendor: "Webstaurant", packSize: "1 10 lb", brand: "YC", item: "sprinkles, Yum Crumbs lemon", unit: "ozs", totalWeightOz: 64, pricePerPkg: 28.89, perLbPint: 2.70, perOzUnit: 0.17, notes: "", par: 0, onHand: 0 },

  // Syrups / Toppings
  { id: 59, category: "FOOD", vendor: "SGC", packSize: "6 66 oz", brand: "Lyon's", item: "syrup, caramel sauce", unit: "ozs", totalWeightOz: 396, pricePerPkg: 36.89, perLbPint: 0.25, perOzUnit: 0.58, notes: "$16.84/ea", par: 0, onHand: 0 },
  { id: 60, category: "FOOD", vendor: "SGC", packSize: "1 48 oz", brand: "Hershey's", item: "syrup, chocolate", unit: "ozs", totalWeightOz: 48, pricePerPkg: 74.58, perLbPint: 3.01, perOzUnit: 0.19, notes: "", par: 0, onHand: 0 },
  { id: 61, category: "FOOD", vendor: "SGC", packSize: "6 36 oz", brand: "Jubilee", item: "syrup, fudge", unit: "ozs", totalWeightOz: 753, pricePerPkg: 71.14, perLbPint: 2.38, perOzUnit: 0.15, notes: "", par: 0, onHand: 0 },
  { id: 62, category: "FOOD", vendor: "SGC", packSize: "6 10#", brand: "Jubilee", item: "syrup, marshmallow cream", unit: "ozs", totalWeightOz: 218, pricePerPkg: 101.02, perLbPint: 2.16, perOzUnit: 0.13, notes: "", par: 0, onHand: 0 },
  { id: 63, category: "FOOD", vendor: "SGC", packSize: "6 36 oz", brand: "Lyon's", item: "syrup, peanut butter topping", unit: "ozs", totalWeightOz: 318, pricePerPkg: 45.04, perLbPint: 3.34, perOzUnit: 0.21, notes: "", par: 0, onHand: 0 },
  { id: 64, category: "FOOD", vendor: "Webstaurant", packSize: "3 10# cans", brand: "Lyon's", item: "syrup, peanut sundae topping", unit: "ozs", totalWeightOz: 318, pricePerPkg: 122.49, perLbPint: 8.16, perOzUnit: 0.39, notes: "", par: 0, onHand: 0 },
  { id: 65, category: "FOOD", vendor: "Webstaurant", packSize: "3 1/2 gal", brand: "Berry", item: "topping, black raspberry sundae", unit: "jar", totalWeightOz: 316, pricePerPkg: 121.87, perLbPint: 6.13, perOzUnit: 0.39, notes: "$44.99/ea", par: 0, onHand: 0 },

  // Whipped Cream / Yogurt
  { id: 66, category: "FOOD", vendor: "SGC", packSize: "12 16 oz", brand: "ReddiWhip", item: "whipped cream, aerosol", unit: "each", totalWeightOz: 12, pricePerPkg: 50.87, perLbPint: 5.12, perOzUnit: 0.28, notes: "", par: 0, onHand: 0 },
  { id: 67, category: "FOOD", vendor: "Walmart", packSize: "1 7 oz", brand: "ReddiWhip", item: "whipped cream, non dairy", unit: "each", totalWeightOz: 7, pricePerPkg: 4.64, perLbPint: 4.24, perOzUnit: 0.68, notes: "", par: 0, onHand: 0 },
  { id: 68, category: "FOOD", vendor: "Walmart", packSize: "1 32 oz", brand: "Great Value", item: "yogurt, plain", unit: "ozs", totalWeightOz: 32, pricePerPkg: 2.78, perLbPint: 1.38, perOzUnit: 0.09, notes: "", par: 0, onHand: 0 },

  // ===== PAPERGOODS =====
  { id: 69, category: "PAPERGOODS", vendor: "Trash", packSize: "1 4 ct", brand: "", item: "pup cup, prepared", unit: "each", totalWeightOz: 0, pricePerPkg: 0.55, perLbPint: 0, perOzUnit: 73.80, notes: "", par: 0, onHand: 0 },
  { id: 70, category: "PAPERGOODS", vendor: "Bloc-Chic", packSize: "1 1000 ct", brand: "Bloc-Chic", item: "paper fly cups, 6 oz regular", unit: "each", totalWeightOz: 1000, pricePerPkg: 73.80, perLbPint: 0, perOzUnit: 0.07, notes: "", par: 0, onHand: 0 },
  { id: 71, category: "PAPERGOODS", vendor: "Visstun", packSize: "1 1000 ct", brand: "Visstun", item: "paper cups, 3 oz yellow", unit: "each", totalWeightOz: 1000, pricePerPkg: 124.33, perLbPint: 0, perOzUnit: 0.12, notes: "", par: 0, onHand: 0 },
  { id: 72, category: "PAPERGOODS", vendor: "Visstun", packSize: "1 1000 ct", brand: "Visstun", item: "paper cups, 6 oz blue", unit: "each", totalWeightOz: 1000, pricePerPkg: 141.52, perLbPint: 0, perOzUnit: 0.14, notes: "", par: 0, onHand: 0 },
  { id: 73, category: "PAPERGOODS", vendor: "Visstun", packSize: "1 1000 ct", brand: "Visstun", item: "paper cups, 8 oz", unit: "each", totalWeightOz: 1000, pricePerPkg: 134.00, perLbPint: 0, perOzUnit: 0.13, notes: "", par: 0, onHand: 0 },
  { id: 74, category: "PAPERGOODS", vendor: "Visstun", packSize: "2 1000 ct", brand: "Visstun", item: "dome lid, 3 oz yellow cup", unit: "each", totalWeightOz: 1000, pricePerPkg: 245.00, perLbPint: 0, perOzUnit: 0.25, notes: "", par: 0, onHand: 0 },
  { id: 75, category: "PAPERGOODS", vendor: "Visstun", packSize: "2 1000 ct", brand: "Visstun", item: "dome lid, 6 oz blue cup", unit: "each", totalWeightOz: 1000, pricePerPkg: 54.89, perLbPint: 0, perOzUnit: 0.05, notes: "", par: 0, onHand: 0 },
  { id: 76, category: "PAPERGOODS", vendor: "Webstaurant", packSize: "20", brand: "Rest Market", item: "plastic cold cup, 16 oz clear", unit: "each", totalWeightOz: 1000, pricePerPkg: 35.49, perLbPint: 0, perOzUnit: 0.04, notes: "", par: 0, onHand: 0 },
  { id: 77, category: "PAPERGOODS", vendor: "SGC", packSize: "20", brand: "50 Choice", item: "dome lids, 16 oz w hole", unit: "each", totalWeightOz: 2500, pricePerPkg: 38.00, perLbPint: 0, perOzUnit: 0.01, notes: "", par: 0, onHand: 0 },
  { id: 78, category: "PAPERGOODS", vendor: "SGC", packSize: "1 2500 ct", brand: "Rest Market", item: "portion cups, 2 oz black", unit: "each", totalWeightOz: 2500, pricePerPkg: 28.38, perLbPint: 0, perOzUnit: 0.01, notes: "", par: 0, onHand: 0 },
  { id: 79, category: "PAPERGOODS", vendor: "SGC", packSize: "1 2500 ct", brand: "Rest Market", item: "portion cup lid, 2 oz clear", unit: "each", totalWeightOz: 2500, pricePerPkg: 25.67, perLbPint: 0, perOzUnit: 0.01, notes: "", par: 0, onHand: 0 },

  // ===== JOB SUPPLIES =====
  { id: 80, category: "JOB SUPPLIES", vendor: "Sam's", packSize: "1 300 ct", brand: "Member's Mark", item: "plastic water cups, free", unit: "each", totalWeightOz: 300, pricePerPkg: 10.88, perLbPint: 0, perOzUnit: 0.04, notes: "", par: 0, onHand: 0 },
  { id: 81, category: "JOB SUPPLIES", vendor: "Amazon", packSize: "10 100 ct", brand: "", item: "spoons, color changing", unit: "pack", totalWeightOz: 1000, pricePerPkg: 55.80, perLbPint: 5.58, perOzUnit: 0.06, notes: "", par: 0, onHand: 0 },
  { id: 82, category: "JOB SUPPLIES", vendor: "Webstaurant", packSize: "1 1500 ct", brand: "", item: "spoons, taster", unit: "pack", totalWeightOz: 1500, pricePerPkg: 50.49, perLbPint: 0, perOzUnit: 0.03, notes: "", par: 0, onHand: 0 },
  { id: 83, category: "JOB SUPPLIES", vendor: "Webstaurant", packSize: "1 300 ct", brand: "", item: "forks, clear plastic", unit: "pack", totalWeightOz: 300, pricePerPkg: 14.98, perLbPint: 0, perOzUnit: 0.05, notes: "", par: 0, onHand: 0 },
  { id: 84, category: "JOB SUPPLIES", vendor: "Webstaurant", packSize: "1 500 ct", brand: "", item: "straws, neon colossal", unit: "pack", totalWeightOz: 300, pricePerPkg: 26.99, perLbPint: 11.25, perOzUnit: 0.09, notes: "", par: 0, onHand: 0 },
  { id: 85, category: "JOB SUPPLIES", vendor: "Webstaurant", packSize: "1 300 ct", brand: "500 Choice", item: "cup carrier", unit: "case", totalWeightOz: 300, pricePerPkg: 89.99, perLbPint: 0, perOzUnit: 0.02, notes: "", par: 0, onHand: 0 },
  { id: 86, category: "JOB SUPPLIES", vendor: "Webstaurant", packSize: "500", brand: "300 Choice", item: "foil bags, insulated", unit: "case", totalWeightOz: 4000, pricePerPkg: 38.49, perLbPint: 0, perOzUnit: 0.13, notes: "", par: 0, onHand: 0 },
  { id: 87, category: "JOB SUPPLIES", vendor: "SGC", packSize: "24 250 ct", brand: "Dixie Ultra", item: "napkins, 2-ply brown", unit: "pack", totalWeightOz: 500, pricePerPkg: 68.49, perLbPint: 0, perOzUnit: 0.13, notes: "", par: 0, onHand: 0 },

  // ===== NOT FOR INVENTORY =====
  { id: 88, category: "NOT FOR INVENTORY", vendor: "State Fair", packSize: "1 1000 ct", brand: "Nat'l Checking", item: "paper bags, donut/sugar shaker bag", unit: "roll", totalWeightOz: 1000, pricePerPkg: 62.25, perLbPint: 0, perOzUnit: 0.08, notes: "", par: 0, onHand: 0 },
  { id: 89, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "1 30 ct", brand: "Penguar", item: "receipt paper, thermal", unit: "roll", totalWeightOz: 30, pricePerPkg: 69.27, perLbPint: 2.31, perOzUnit: 0, notes: "lower price!", par: 0, onHand: 0 },
  { id: 90, category: "NOT FOR INVENTORY", vendor: "Walmart", packSize: "1 100 ct", brand: "", item: "envelopes", unit: "pack", totalWeightOz: 100, pricePerPkg: 1.97, perLbPint: 0.02, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 91, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "10 100 ct", brand: "Companions", item: "gloves, nitrile black small", unit: "pack", totalWeightOz: 10, pricePerPkg: 37.00, perLbPint: 3.70, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 92, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "10 100 ct", brand: "Companions", item: "gloves, nitrile black medium", unit: "pack", totalWeightOz: 10, pricePerPkg: 37.00, perLbPint: 3.70, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 93, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "10 100 ct", brand: "Companions", item: "gloves, nitrile black large", unit: "pack", totalWeightOz: 10, pricePerPkg: 37.00, perLbPint: 3.70, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 94, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "10 100 ct", brand: "Companions", item: "gloves, nitrile black extra large", unit: "pack", totalWeightOz: 10, pricePerPkg: 37.00, perLbPint: 3.70, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 95, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "36 1000 ct", brand: "Compact", item: "toilet tissue, coreless", unit: "pack", totalWeightOz: 36, pricePerPkg: 80.55, perLbPint: 2.24, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 96, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "8 800 ft", brand: "EnMotion", item: "towel roll, EnMotion brown 10 in", unit: "roll", totalWeightOz: 8, pricePerPkg: 76.00, perLbPint: 12.67, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 97, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "10 25 ct", brand: "Berry", item: "trash bags, 23 gal clear plastic", unit: "each", totalWeightOz: 10, pricePerPkg: 42.44, perLbPint: 4.25, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 98, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "3 10# cans", brand: "Lyon's", item: "hand soap, foam w moisturizers", unit: "each", totalWeightOz: 316, pricePerPkg: 50.34, perLbPint: 3.34, perOzUnit: 0.21, notes: "", par: 0, onHand: 0 },
  { id: 99, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "2 1000 mL", brand: "EnMotion", item: "hand sanitizer, foam", unit: "each", totalWeightOz: 318, pricePerPkg: 74.38, perLbPint: 8.16, perOzUnit: 0.39, notes: "", par: 0, onHand: 0 },
  { id: 100, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "2 2 L", brand: "Swisher", item: "cleaner, glass", unit: "gal", totalWeightOz: 64, pricePerPkg: 76.41, perLbPint: 6.12, perOzUnit: 0.32, notes: "", par: 0, onHand: 0 },
  { id: 101, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "2 2 L", brand: "Swisher", item: "cleaner, floor neutral", unit: "gal", totalWeightOz: 0, pricePerPkg: 70.73, perLbPint: 5.12, perOzUnit: 0.32, notes: "", par: 0, onHand: 0 },
  { id: 102, category: "NOT FOR INVENTORY", vendor: "Swift Freeze", packSize: "1 1 gal", brand: "Swisher", item: "sanitizer, T-san (machine sani)", unit: "gal", totalWeightOz: 0, pricePerPkg: 20.48, perLbPint: 0, perOzUnit: 0, notes: "complimentary bottle w purchase", par: 0, onHand: 0 },
  { id: 103, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "1 1 gal", brand: "", item: "sanitizer, Sani-quad", unit: "gal", totalWeightOz: 0, pricePerPkg: 25.17, perLbPint: 0, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 104, category: "NOT FOR INVENTORY", vendor: "SGC", packSize: "1 9 ct", brand: "Glade", item: "air fresheners, plug-ins", unit: "each", totalWeightOz: 0, pricePerPkg: 105.8, perLbPint: 0, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 105, category: "NOT FOR INVENTORY", vendor: "Walmart", packSize: "1 75 oz", brand: "Dawn", item: "soap, dish soap (kitchen)", unit: "each", totalWeightOz: 48, pricePerPkg: 17.97, perLbPint: 0, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 106, category: "NOT FOR INVENTORY", vendor: "Sam's", packSize: "1 105 ct", brand: "Member's Mark", item: "soap, dishwasher tabs", unit: "each", totalWeightOz: 105, pricePerPkg: 5.98, perLbPint: 0, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
  { id: 107, category: "NOT FOR INVENTORY", vendor: "Walmart", packSize: "2 24 oz", brand: "Great Value", item: "toilet bowl cleaner", unit: "each", totalWeightOz: 48, pricePerPkg: 12.88, perLbPint: 0, perOzUnit: 0, notes: "", par: 0, onHand: 0 },
];
