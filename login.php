<?php
include 'verify.php';

if (verify_session()) {
    header('Location: /');
    die();
}

session_start();
if (empty($_SESSION['token'])) {
    $_SESSION['token'] = bin2hex(random_bytes(32));
}

$message = '';
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if ( $_POST['token'] == $_SESSION['token'] &&
        md5($_POST['username']) == '' &&
        md5($_POST['password']) == ''
    ) {
        $insert = $pdo->prepare("INSERT INTO sessions
            VALUES(:id, :ua, :ip, NOW() + interval 4 hour);");
        $session_id = bin2hex(random_bytes(32));
        $insert->execute([':id' => $session_id, ':ua' => $ua, ':ip' => $ip]);
        $pdo->commit();
        setcookie('session_id', $session_id, time() + (60 * 60 * 4), "/");
        header('Location: /');
    } else {
        $message = 'Failed login';
    }
}

?>
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Log In</title>
    <link href="login.css" rel="stylesheet" />
  </head>
  <body>
    <form action="login.php" method="post">
      <div class="container">
        <div> <img src="icon_shadow.png" alt="" height="70" width="70"> </div>
        <label for="username">Username</label>
        <input
          type="text"
          name="username"
          id="username"
          autocomplete="username"
          required
        />
        <label for="password">Password</label>
        <input
          type="password"
          name="password"
          id="password"
          required
        />
        <input type="hidden" name="token" value="<?php echo $_SESSION['token']; ?>" required/>
        <button type="submit">Log In</button>
      </div>
    <h2><?php echo $message ?></h2>
    </form>
  </body>
  <link rel="prefetch" href="style.css">
  <link rel="prefetch" href="main.js">
</html>
