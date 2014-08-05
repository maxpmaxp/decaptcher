<head>
<title>Decaptcha stats</title>

<style type="text/css">
table {
    font-family: verdana,arial,sans-serif;
    font-size: 11px;
    color: #333333;
    border-width: 1px;
    border-color: #666666;
    border-collapse: collapse;
    margin: auto;
    margin-top: 20px;
}
th, td {
    padding: 5 10px;
    border: 1px solid #666666;
}
th {
    background-color: #dedede;
}
</style>
</head>

<body>

<table>
    <tr>
        <th>Service</th>
        <th>Successful</th>
        <th>Fails</th>
        <th>Balance</th>
        <th>Date of last charge</th>
    </tr>

    % for service in uses:
    <tr>
        <td>{{ service }}</td>
        <td>{{ uses[service] - fails[service] }}</td>
        <td>{{ fails[service] }}</td>
        <td>{{ balances[service] or '-' }}</td>
        <td>{{ last_charge_dates[service] }}</td>
    </tr>
    % end
</table>

</body>
