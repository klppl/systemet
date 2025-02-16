<?php
// Open the SQLite database
$db = new SQLite3('products.db');

// Query the products. The DataTables ordering will override this order.
$results = $db->query('SELECT * FROM products');
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Systemet</title>
  <!-- DataTables CSS -->
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
    }
    table.dataTable thead th,
    table.dataTable thead td {
      border-bottom: 1px solid #ddd;
    }
  </style>
</head>
<body>
  <h1>Systemet</h1>
  <table id="productsTable" class="display" style="width:100%">
    <thead>
      <tr>
        <th>Artikelnummer</th>
        <th>Namn</th>
        <th>Namn 2</th>
        <th>Bryggeri</th>
        <th>APK</th>
        <th>Pris</th>
        <th>Volym</th>
        <th>Alkohol %</th>
        <th>Kategori 1</th>
        <th>Kategori 2</th>
        <th>Kategori 3</th>
        <th>Land</th>
        <th>Lansering</th>
      </tr>
    </thead>
    <tbody>
      <?php while ($row = $results->fetchArray(SQLITE3_ASSOC)): ?>
      <tr>
        <td>
          <a href="https://systembolaget.se/<?php echo htmlspecialchars($row['productNumber']); ?>" target="_blank">
            <?php echo htmlspecialchars($row['productNumber']); ?>
          </a>
        </td>
        <td><?php echo htmlspecialchars($row['productNameBold']); ?></td>
        <td><?php echo htmlspecialchars($row['productNameThin']); ?></td>
        <td><?php echo htmlspecialchars($row['supplierName']); ?></td>
        <td><?php echo htmlspecialchars($row['apk']); ?></td>
        <td><?php echo htmlspecialchars($row['price']); ?></td>
        <td><?php echo htmlspecialchars($row['volume']); ?></td>
        <td><?php echo htmlspecialchars($row['alcoholPercentage']); ?></td>
        <td><?php echo htmlspecialchars($row['categoryLevel1']); ?></td>
        <td><?php echo htmlspecialchars($row['categoryLevel2']); ?></td>
        <td><?php echo htmlspecialchars($row['categoryLevel3']); ?></td>
        <td><?php echo htmlspecialchars($row['country']); ?></td>
        <td><?php echo htmlspecialchars($row['productLaunchDate']); ?></td>
      </tr>
      <?php endwhile; ?>
    </tbody>
  </table>

  <!-- jQuery -->
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <!-- DataTables JS -->
  <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
  <script>
    $(document).ready(function() {
      // Initialize DataTables with 25 entries per page and sort by the APK column (index 4) in descending order.
      $('#productsTable').DataTable({
        pageLength: 25,
        order: [[4, "desc"]]
      });
    });
  </script>
</body>
</html>
