<?php
// 获取传递过来的历史记录
$history = $_POST['history'];

// 连接MySQL数据库
$servername = "localhost"; // 数据库主机名
$username = "root"; // 数据库用户名
$password = ""; // 数据库密码
$dbname = "calculator"; // 数据库名

$conn = new mysqli($servername, $username, $password, $dbname);

// 检查数据库连接是否成功
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// 检查是否已经存在'calculation'列
$sql_check = "SELECT COUNT(*) as count FROM information_schema.columns WHERE table_name = 'history' AND column_name = 'calculation'";
$result_check = $conn->query($sql_check);
if ($result_check->fetch_assoc()['count'] == 0) {
    // 执行 ALTER TABLE 语句以添加'calculation'列
    $sql_alter = "ALTER TABLE history ADD calculation VARCHAR(255)";
    if ($conn->query($sql_alter) === TRUE) {
        echo "成功添加 'calculation' 列到表中";
    } else {
        echo "添加 'calculation' 列时出错: " . $conn->error;
    }
}

// 将历史记录插入数据库中
$sql_insert = "INSERT INTO history (expression) VALUES ('$history')";

if ($conn->query($sql_insert) === TRUE) {
    echo "History saved successfully";
} else {
    echo "Error saving history: " . $conn->error;
}

$conn->close();
?>