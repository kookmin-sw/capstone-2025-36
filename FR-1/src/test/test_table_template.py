tables = [
    '''
    <table>
    <tr>
        <th>Column 1</th>
        <th>Column 2</th>
        <th>Column 3</th>
    </tr>
    <tr>
        <td>Cell 1</td>
        <td>Cell 2</td>
        <td>Cell 3</td>
    </tr>
    <tr>
        <td colspan="3">This cell spans all columns</td>
    </tr>
    </table>
    ''',
    """
    <table border="1">
    <thead>
        <tr>
        <th rowspan="2">이름</th>
        <th colspan="2">인적사항</th>
        <th rowspan="2">메모</th>
        </tr>
        <tr>
        <th>나이</th>
        <th>직업</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <td>김철수</td>
        <td>28</td>
        <td>개발자</td>
        <td rowspan="2">우수 사원</td>
        </tr>
        <tr>
        <td>이영희</td>
        <td>32</td>
        <td>디자이너</td>
        </tr>
        <tr>
        <td>박지민</td>
        <td>25</td>
        <td>마케터</td>
        <td>신입</td>
        </tr>
    </tbody>
    </table>
    """,
"""
<table>
  <tr>
    <th>Name</th>
    <th>Age</th>
  </tr>
  <tr>
    <td>Jane Doe</td>
    <td>25</td>
  </tr>
  <tr>
    <td colspan="2" rowspan="2">This cell spans rows and columns</td>
  </tr>
  <tr>
    <td>John Smith</td>
    <td>30</td>
  </tr>
</table>
""",
"""
<table>
  <tr>
    <th>Subject</th>
    <th>Teacher</th>
    <th>Grade</th>
  </tr>
  <tr>
    <td colspan="2">Math</td>
    <td>85%</td>
  </tr>
  <tr>
    <td>Science</td>
    <td>Ms. Johnson</td>
    <td>90%</td>
  </tr>
  <tr>
    <td>History</td>
    <td colspan="2">Mr. Smith</td>
  </tr>
</table>
""",
"""
<table>
  <tr>
    <th>Name</th>
    <th>Age</th>
  </tr>
  <tr>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Jane Doe</td>
    <td>25</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
  </tr>
</table>
"""
]