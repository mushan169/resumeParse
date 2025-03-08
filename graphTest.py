from py2neo import Graph
import json

# 配置Neo4j连接
graph = Graph("bolt://localhost:7687", auth=("neo4j", "mushanmushan"))

def get_node_id(category, props):
    """根据节点类别和属性生成唯一ID"""
    if category == "Company":
        return props.get("name", "")
    elif category == "CompanyPosition":
        return props.get("id", "")
    elif category in ["Position", "Skill", "Education", "Salary", "Quality", "ActiveTime", "City", "Address"]:
        return props.get("name", "")
    else:
        return str(props.get("id", props.get("name", "")))

def get_graph_data():
    # 查询所有节点
    nodes = []
    node_id_map = {}
    categories = {}

    nodes_query = graph.run("MATCH (n) RETURN labels(n) as labels, properties(n) as props")
    for record in nodes_query:
        labels = record["labels"]
        if not labels:
            continue
        category = labels[0]
        props = record["props"]
        
        node_id = get_node_id(category, props)
        if not node_id or node_id in node_id_map:
            continue
        
        # 确定显示名称
        if category == "CompanyPosition":
            display_name = props.get("id", node_id)
        else:
            display_name = props.get("name", node_id)
        
        # 记录类别
        if category not in categories:
            categories[category] = len(categories)
        
        nodes.append({
            "id": node_id,
            "name": display_name,
            "category": categories[category]
        })
        node_id_map[node_id] = True  # 标记ID已存在

    # 查询所有关系
    links = []
    rels_query = graph.run("""
        MATCH (s)-[r]->(t)
        RETURN 
            labels(s) as s_labels, 
            properties(s) as s_props,
            type(r) as rel_type,
            labels(t) as t_labels,
            properties(t) as t_props
    """)
    
    for record in rels_query:
        s_labels = record["s_labels"]
        s_props = record["s_props"]
        rel_type = record["rel_type"]
        t_labels = record["t_labels"]
        t_props = record["t_props"]
        
        if not s_labels or not t_labels:
            continue
        s_category = s_labels[0]
        t_category = t_labels[0]
        
        # 获取源节点和目标节点的ID
        s_id = get_node_id(s_category, s_props)
        t_id = get_node_id(t_category, t_props)
        
        if s_id in node_id_map and t_id in node_id_map:
            links.append({
                "source": s_id,
                "target": t_id,
                "name": rel_type
            })
    
    # 构建类别列表
    categories_list = [{"name": name} for name in categories.keys()]
    
    return {"nodes": nodes, "links": links, "categories": categories_list}



def get_fuzzy_graph_data(keyword,limit = 30):
    """
    根据关键字模糊查询 CompanyPosition 节点及与其步长为1的相邻节点
    这里假设 CompanyPosition 节点的 id 或 name 字段用于匹配关键字
    """
    # 用于存放节点、关系和类别
    nodes = {}       # 使用字典防止重复，键为 node_id
    links = []
    categories = {}

    # 这里使用 Cypher 查询：先匹配 CompanyPosition 节点（模糊匹配 id 或 name）
    # 然后通过 OPTIONAL MATCH 查找与该节点相连的所有节点（步长为1）
    query = """
    MATCH (n:CompanyPosition)
    WHERE n.id CONTAINS $keyword OR n.name CONTAINS $keyword
    with n limit $limit
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN n, r, m, type(r) AS rel_type
    """
    results = graph.run(query, keyword=keyword,limit = limit)
    
    for record in results:
        # 处理起始节点 n
        node_n = record["n"]
        if node_n is not None:
            labels_n = list(node_n.labels)
            category_n = labels_n[0] if labels_n else "Undefined"
            props_n = dict(node_n)
            node_id_n = get_node_id(category_n, props_n)
            if node_id_n not in nodes:
                # 针对 CompanyPosition 节点显示 id，否则显示 name
                if category_n == "CompanyPosition":
                    display_name_n = props_n.get("id", node_id_n)
                else:
                    display_name_n = props_n.get("name", node_id_n)
                # 如果该类别还未记录，则添加
                if category_n not in categories:
                    categories[category_n] = len(categories)
                nodes[node_id_n] = {
                    "id": node_id_n,
                    "name": display_name_n,
                    "category": categories[category_n]
                }
        
        # 处理与 n 相连的邻居节点 m
        node_m = record["m"]
        if node_m is not None:
            labels_m = list(node_m.labels)
            category_m = labels_m[0] if labels_m else "Undefined"
            props_m = dict(node_m)
            node_id_m = get_node_id(category_m, props_m)
            if node_id_m not in nodes:
                display_name_m = props_m.get("name", node_id_m)
                if category_m not in categories:
                    categories[category_m] = len(categories)
                nodes[node_id_m] = {
                    "id": node_id_m,
                    "name": display_name_m,
                    "category": categories[category_m]
                }
        
        # 处理两节点之间的关系
        rel = record["r"]
        rel_type = record["rel_type"]
        # 只有当关系存在且两端节点都有数据时，才加入关系记录
        if rel is not None and node_n is not None and node_m is not None and rel_type:
            s_labels = list(node_n.labels)
            t_labels = list(node_m.labels)
            s_category = s_labels[0] if s_labels else "Undefined"
            t_category = t_labels[0] if t_labels else "Undefined"
            s_id = get_node_id(s_category, dict(node_n))
            t_id = get_node_id(t_category, dict(node_m))
            links.append({
                "source": s_id,
                "target": t_id,
                "name": rel_type
            })
    # 构建类别列表
    categories_list = [{"name": name} for name in categories.keys()]
    
    return {"nodes": list(nodes.values()), "links": links, "categories": categories_list}

if __name__ == '__main__':
    keyword = "华为"  # 根据需要修改为实际查询关键字
    data = get_fuzzy_graph_data(keyword)
    # 将结果写入 JSON 文件
    print(data["links"])
    with open('GraphData_fuzzy.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
