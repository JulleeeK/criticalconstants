import mysql.connector
import os
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
driver = 'ODBC Driver 18 for SQL Server'

def literature_search(ligandID, metalID):
    cnxn = mysql.connector.connect(host='host', database='sb', user='u', password='p')
    cursor = cnxn.cursor()
    cursor.execute("SELECT literature_altNR FROM verkn_ligand_metal_literature WHERE ligandenNr=\"" + ligandID + "\" and metalNr=\"" + metalID +"\"")
    result = []
    for row in cursor:
        result.append(row)
    Literature_string = ""
    for row in result:
            cursor.execute(
                "SELECT literature_alt FROM literature_alt WHERE literature_altID=\"" + str(row[0]) + "\"")
            for f in cursor:
                Literature_string += "<p>" + str(f[0]) + "</p>"
    return Literature_string


@app.route("/", methods = ["GET", "POST"])
def critical():
    ligand_ret_data = ""
    metal_ret_data = ""
    lig_def = ""
    metal_def = ""
    const_ret_data = ""
    posmetals_temp = ""
    posmetals = "<option value=\"\"></option>"
    # check if search was pressed
    if request.method == "POST":
        lig_def = request.form.get("value")
        metal_def = request.form.get("metal")
        # check if value is set
        if request.form.get("value") != "":
            # establish connection to sql server
            cnxn = mysql.connector.connect(host='host', database='db', user='u', password='p')
            cursor = cnxn.cursor()
            # handle ligands
            value_ligand = request.form.get("value")
            ligand_id = ""
            metal_id = ""
            lig_data = ""

            # make formal search easy
            if (request.form.get("table") == "formula") and (len(value_ligand.split(" ")) > 1):
                i = 0
                temp_value_ligand = ""
                for entry in value_ligand.split(" "):
                    if i == (len(value_ligand.split(" ")) - 1):
                        temp_value_ligand += entry
                    else:
                        temp_value_ligand += entry + "%\" and formula LIKE \"%"
                    i += 1
                value_ligand = temp_value_ligand
            # sql query for ligand and formatting
            cursor.execute("SELECT name_ligand, formula, ligandenID FROM liganden WHERE " + request.form.get("table") + " LIKE \"%" + value_ligand + "%\"")
            i = 0
            for row in cursor:

                lig_data += "<p>name: <span id=\"DIVtext"+str(i)+"\" style=\"text-decoration: underline;\"" \
                            "onClick=\"CopyDIV(this.id)\">" + str(row[0]) + "</span> formula: " + str(row[1]) + "</p>"
                ligand_id = int(row[2])
                i += 1
            # searching for possible metalIDs
            cursor.execute("SELECT metalNr FROM verkn_ligand_metal WHERE ligandenNr=\"" + str(ligand_id) + "\"")
            # handling metal
            metal_list = []
            posmetallist = []
            for row in cursor:
                if str(row[0]) not in metal_list:
                    metal_list.append(str(row[0]))
            for row in metal_list:
                cursor.execute("SELECT name_metal, name_metal_pur FROM metal WHERE metalID=\"" + str(row) + "\"")
                for r in cursor:
                    posmetallist.append(str(r[1]) + " " + str(r[0]))
            posmetallist.sort()
            for row in posmetallist:
                posmetals_temp += "<option value=" + row.split(" ")[0] + ">" + row.split(" ")[1] + "</option>"
            metal_data = ""
            name_metal = request.form.get("metal")
            if i == 1:
                posmetals += posmetals_temp
            # check if lig results are definite
            if i == 1 and request.form.get("metal"):
                metal_query = "SELECT name_metal, name_metal_pur, metalID FROM metal WHERE name_metal_pur=\"" + name_metal + "\""
                # metal sql query and formatting
                cursor.execute(metal_query)
                f = 0
                for row in cursor:
                    metal_data += "<p>" + str(row[0]) + ", " + str(row[1]) + "</p>"
                    metal_id = int(row[2])
                    f += 1
                metal_ret_data = metal_data
                if f == 1:
                    # search for verkn
                    res_data = []
                    cursor.execute("SELECT * FROM verkn_ligand_metal WHERE ligandenNr=\"" + str(ligand_id) + "\" and metalNr=\"" + str(metal_id) + "\"")
                    # formatting for normal data
                    for row in cursor:
                        res_data.append(row)
                    for row in res_data:
                        if str(row[7]) == str(row[8]):
                            cursor.execute("SELECT name_beta_definition FROM beta_definition WHERE beta_definitionID=\"" + str(row[3]) + "\"")
                            for r in cursor:
                                const_ret_data += "<p> " + str(r[0] + "&nbsp;")
                            cursor.execute(
                                "SELECT name_constanttyp FROM constanttyp WHERE constanttypID=\"" + str(row[4]) + "\"")
                            for r in cursor:
                                if str(r[0]) == "K":
                                    const_ret_data += " logK "
                                    const_ret_data += str(row[7])
                                    const_ret_data += "(" + str(row[9]) + ") "
                                elif str(r[0]) == "H":
                                    const_ret_data += " &#916H "
                                    const_ret_data += str(row[8])
                                    const_ret_data += "kcal/mol "
                                    const_ret_data += str(row[7])
                                    const_ret_data += "kJ/mol "
                                elif str(r[0]) == "S":
                                    const_ret_data += " &#916S "
                                    const_ret_data += str(row[8])
                                    const_ret_data += "kcal/mol "
                                    const_ret_data += str(row[7])
                                    const_ret_data += "J/kmol "
                            const_ret_data += "&nbsp; " + str(row[5]) + "&#8451&nbsp;"
                            const_ret_data += " &#956; " + str(row[6])
                            cursor.execute(
                                "SELECT name_footnote FROM footnote WHERE footnoteID=\"" + str(row[10]) + "\"")
                            for r in cursor:
                                const_ret_data += " comment: " + str(r[0])
                            const_ret_data += "</p>"
                        else:
                            cursor.execute(
                                "SELECT name_beta_definition FROM beta_definition WHERE beta_definitionID=\"" + str(
                                    row[3]) + "\"")
                            for r in cursor:
                                const_ret_data += "<p><b> " + str(r[0]) + "&nbsp;"
                            cursor.execute(
                                "SELECT name_constanttyp FROM constanttyp WHERE constanttypID=\"" + str(row[4]) + "\"")
                            for r in cursor:
                                if str(r[0]) == "K":
                                    const_ret_data += " logK "
                                    const_ret_data += str(row[7])
                                    const_ret_data += "(" + str(row[9]) + ") "
                                elif str(r[0]) == "H":
                                    const_ret_data += " &#916H "
                                    const_ret_data += str(row[8])
                                    const_ret_data += "kcal/mol "
                                    const_ret_data += str(row[7])
                                    const_ret_data += "kJ/mol "
                                elif str(r[0]) == "S":
                                    const_ret_data += " &#916S "
                                    const_ret_data += str(row[8])
                                    const_ret_data += "kcal/mol "
                                    const_ret_data += str(row[7])
                                    const_ret_data += "J/kmol "
                            const_ret_data += "&nbsp; " + str(row[5]) + "&#8451&nbsp;"
                            const_ret_data += " &#956; " + str(row[6])
                            cursor.execute(
                                "SELECT name_footnote FROM footnote WHERE footnoteID=\"" + str(row[10]) + "\"")
                            for r in cursor:
                                const_ret_data += " comment: " + str(r[0])
                            const_ret_data += "</b></p>"
                    # literature
                    literature = literature_search(str(ligand_id), str(metal_id))
                    const_ret_data += "<p>Literature: " + literature + "</p>"
            cnxn.close()
            ligand_ret_data = lig_data
            # checks if there are entries in database for everything
            if ligand_ret_data == "":
                ligand_ret_data = "There is no entry in the Database for this ligand. Please try a different one."
            if request.form.get("metal") != "":
                if metal_ret_data == "":
                    metal_ret_data = "There is no entry in the Database for this metal. Please try a different one."
        return render_template('NISTSRD46.html', ligand_data=ligand_ret_data, metal_data=metal_ret_data, default_lig=lig_def, default_metal=metal_def, constant_data=const_ret_data, pos_metals=posmetals)
    return render_template('NISTSRD46.html', ligand_data=ligand_ret_data, metal_data=metal_ret_data, default_lig=lig_def, default_metal=metal_def, constant_data=const_ret_data, pos_metals=posmetals)



if __name__ == "__main__":
    app.run(host="0.0.0.0")
