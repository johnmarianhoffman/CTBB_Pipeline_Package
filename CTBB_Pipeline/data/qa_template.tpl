<!DOCTYPE html>
<html>
    <body>

        <!-- Set up main header and links to other dose pages -->
        <h1> {{ curr_dose }}% of clinical dose   </h1>
        {% for d in doses %}
        <a href="results_{{curr_test}}_{{d}}.html">{{d}}%</a>
        {% endfor %}

        <!-- Iterate through each patient -->
        {% for p in internal_ids_fullpath %}
        <hr> </hr>
        <h2>Patient {{p[0]}}</h2>
        <table cellspacing="20">
        
        {% for k in kernels %}        
        <tr>
            <th> Kernel {{k}}</th>
        </tr>
        <tr>
            <td></td>
            {% for sts in slice_thicknesses %}
            <td> {{sts}}</td>
            {% endfor %}
        </tr>


        <!-- put images into doc -->
        <tr>
            <td></td>
            {% for sts in slice_thicknesses %}
            <td><img src="{{library_path}}/recon/{{curr_dose}}/{{p[1]}}_k{{k}}_st{{sts}}/qa/{{curr_test_file}}"></td>
            {% endfor %}
        </tr>

        
        {% endfor %} <!-- kernels -->
        </table>
        {% endfor %} <!-- patients -->


        

    </body>
</html>
