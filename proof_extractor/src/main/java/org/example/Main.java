package org.example;

import de.tu_dresden.inf.lat.evee.general.data.exceptions.FormattingException;
import de.tu_dresden.inf.lat.evee.general.data.exceptions.ParsingException;
import de.tu_dresden.inf.lat.evee.proofs.data.Inference;
import de.tu_dresden.inf.lat.evee.proofs.data.Proof;
import de.tu_dresden.inf.lat.evee.proofs.data.exceptions.ProofGenerationFailedException;
import de.tu_dresden.inf.lat.evee.proofs.interfaces.IInference;
import de.tu_dresden.inf.lat.evee.proofs.interfaces.IProof;
import de.tu_dresden.inf.lat.evee.proofs.json.JsonProofWriter;
import de.tu_dresden.inf.lat.evee.proofs.tools.MinimalProofExtractor;
import de.tu_dresden.inf.lat.evee.proofs.tools.measures.TreeSizeMeasure;
import guru.nidi.graphviz.attribute.Color;
import guru.nidi.graphviz.attribute.Label;
import guru.nidi.graphviz.attribute.Shape;
import guru.nidi.graphviz.attribute.Style;
import guru.nidi.graphviz.engine.Format;
import guru.nidi.graphviz.engine.Graphviz;
import guru.nidi.graphviz.engine.Renderer;
import guru.nidi.graphviz.model.MutableGraph;
import guru.nidi.graphviz.model.MutableNode;
import org.json.simple.JSONArray;
import org.json.simple.parser.ParseException;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

// Press Shift twice to open the Search Everywhere dialog and type `show whitespaces`,
// then press Enter. You can now see whitespace characters in your code.
public class Main {

    private static String GRAPH;
    private static String PROOF;

    private static Color RULE_COLOR = Color.rgb(142,203,240);

    public static void extractProof(SimpleGraph graph, String jsonFile, String svgFile) throws ProofGenerationFailedException, FormattingException, IOException {
        JSONArray edges = graph.getEdges();
        String goal = graph.getConclusion();
        //edges.remove(edges.size()-1);
        IProof<String> proof = new Proof<>(goal);

        for (Object edge : edges) {
            JSONArray e = (JSONArray) edge;
            LinkedList<String> premises = new LinkedList<>();
            JSONArray premisesArray = (JSONArray) e.get(0);
            for (Object premise : premisesArray) {
                premises.add((String) premise);
            }
            Inference<String> inference = new Inference<>((String) e.get(2), (String) e.get(1), premises);
            proof.addInference(inference);
        }
//        draw(proof, GRAPH);
        IProof<String> minTree = new MinimalProofExtractor<>(new TreeSizeMeasure<String>()).extract(proof);
        JsonProofWriter<String> writer = JsonProofWriter.getInstance();
        writer.writeToFile(minTree, jsonFile.replaceAll(".json", ""));
//        System.out.println("TREE:\n" + writer.toString(minTree));
        draw(minTree, svgFile);
    }

    public static <T> void draw(IProof<T> proof, String outFile) throws IOException {
        GraphMLMapper<T> map = new GraphMLMapper<T>();
        Set<IInference<T>> explored = new HashSet<>();
        Map<Integer, MutableNode> id2Node = new HashMap<>();
        Map<Integer,Set<Integer>> node2Nodes = new HashMap<>();

        MutableGraph graph = guru.nidi.graphviz.model.Factory.mutGraph("proof").setDirected(true);

//        MutableNode sink = guru.nidi.graphviz.model.Factory.mutNode(proof.getFinalConclusion().toString())
//                .add(Label.of(proof.getFinalConclusion().toString()), Shape.RECTANGLE,
//                        Style.ROUNDED);

        proof.getInferences().forEach(x->
                populateGraph(graph, x, map, explored, id2Node, node2Nodes)
        );

        Renderer vizRenderer = Graphviz.fromGraph(graph).scale(1.2).totalMemory(24000000).render(Format.SVG);
        File out = new File(outFile);
        vizRenderer.toFile(out);
    }

    private static <T> void populateGraph(MutableGraph graph, IInference<T> currentInference,
                                          GraphMLMapper<T> map, Set<IInference<T>> explored,
                                          Map<Integer, MutableNode> id2Node, Map<Integer,Set<Integer>> node2Nodes) {
        if(explored.contains(currentInference))
            return;
        explored.add(currentInference);

        MutableNode ruleNameNode = getOrCreateEdge(currentInference, graph, map, id2Node);
        // Create premise nodes and their edges
        currentInference.getPremises().forEach(premise -> {
            MutableNode premiseNode = getOrCreateNode(premise, graph, map, id2Node);
            premiseNode.addLink(ruleNameNode);
        });

        if(!node2Nodes.containsKey(map.getInferenceID(currentInference)))
            node2Nodes.put(map.getInferenceID(currentInference), new HashSet<>());

        T conclusionAxiom = currentInference.getConclusion();
        if(!node2Nodes.get(map.getInferenceID(currentInference)).contains(map.getAxiomID(conclusionAxiom))){
            MutableNode conclusionNode = getOrCreateNode(conclusionAxiom, graph, map, id2Node);
            ruleNameNode.addLink(conclusionNode);
            node2Nodes.get(map.getInferenceID(currentInference)).add(map.getAxiomID(conclusionAxiom));
        }
    }

    private static <T> MutableNode getOrCreateEdge(IInference<T> currentInference, MutableGraph graph, GraphMLMapper<T> map, Map<Integer, MutableNode> id2Node) {
        MutableNode ruleNameNode;
        boolean inferenceWasAdded = map.addInferenceEntry(currentInference);
        if(inferenceWasAdded){
            ruleNameNode = guru.nidi.graphviz.model.Factory.mutNode(String.valueOf(map.getInferenceID(currentInference))).add(
                    Label.of(format(currentInference.getRuleName())), Style.combine(Style.FILLED, Style.ROUNDED), RULE_COLOR, Shape.RECTANGLE);
            id2Node.put(map.getInferenceID(currentInference), ruleNameNode);
            graph.add(ruleNameNode);

        }
        else{
            ruleNameNode = id2Node.get(map.getInferenceID(currentInference));
        }
        return ruleNameNode;
    }

    private static <T> MutableNode getOrCreateNode(T axiom, MutableGraph graph, GraphMLMapper<T> map, Map<Integer, MutableNode> id2Node) {
        boolean axiomWasAdded = map.addStatementEntry(axiom);
        MutableNode axiomNode;
        if(axiomWasAdded){
            axiomNode = guru.nidi.graphviz.model.Factory.mutNode(String.valueOf(map.getAxiomID(axiom)))
                    .add(Label.of(format(axiom.toString())), Shape.RECTANGLE, Style.ROUNDED);
            id2Node.put(map.getAxiomID(axiom),axiomNode);
            graph.add(axiomNode);
        }
        else
            axiomNode =  id2Node.get(map.getAxiomID(axiom));
        return axiomNode;
    }

    public static String format (String label) {
        label = label.replaceAll("Boxplus" , "⊞");
        label = label.replaceAll("Boxminus" , "⊟");
        label = label.replaceAll("Diamondplus" , "◇");
        label = label.replaceAll("Diamondminus" , "⟠");
        label = label.replaceAll("\\+inf" , "∞");
        label = label.replaceAll("-inf" , "-∞");
        label = label.replaceAll(":-" , " :- ");
        label = label.replaceAll("," , ", ");
        return label;
    }

    public static void main(String[] args) throws FormattingException, ProofGenerationFailedException, ParsingException, IOException, ParseException {
        // Press Alt+Enter with your caret at the highlighted text to see how
        // IntelliJ IDEA suggests fixing it
        // run the program with path from args
        String inputFile = args[0];
        long startTime = System.nanoTime();
        extractProof(new SimpleGraph(inputFile), args[1], args[2]);
        long endTime = System.nanoTime();
        long timeElapsed = endTime - startTime;
        String time = String.format("%.2f", (double) timeElapsed / 1000000000);
        String toWrite = "File: " + inputFile + ", Time: " + time + "\n";
        try {
            FileWriter fw = new FileWriter("proof_time.txt", true);
            fw.write(toWrite);
            fw.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}