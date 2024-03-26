package org.example;

import org.json.simple.JSONArray;
import org.json.simple.parser.ParseException;
import org.json.simple.JSONObject;
import org.json.simple.parser.*;

import java.io.FileReader;
import java.io.IOException;

public class SimpleGraph {
    private JSONArray edges;
    private String conclusion;

    public SimpleGraph(String path) throws IOException, ParseException {
        Object obj = new JSONParser().parse(new FileReader(path));
        JSONObject jo = (JSONObject) obj;
        this.edges = (JSONArray) jo.get("edges");
        this.conclusion = (String) jo.get("conclusion");
    }

    public JSONArray getEdges() {
        return edges;
    }

    public String getConclusion() {
        return conclusion;
    }
}
