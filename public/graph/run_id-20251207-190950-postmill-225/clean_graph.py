#!/usr/bin/env python3
"""
清理 web_graph.json 中没有对应截图文件的节点和边
"""

import json
import os
from pathlib import Path

def clean_graph(graph_path: str, screenshots_dir: str, output_path: str = None):
    """
    清理图数据，移除没有对应截图的节点和相关边
    
    Args:
        graph_path: web_graph.json 的路径
        screenshots_dir: 截图文件夹路径
        output_path: 输出文件路径，默认覆盖原文件
    """
    # 读取图数据
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph_data = json.load(f)
    
    # 获取截图文件夹中的所有文件名
    screenshot_files = set()
    for file in os.listdir(screenshots_dir):
        if file.endswith('.png'):
            screenshot_files.add(file)
    
    print(f"截图文件夹中共有 {len(screenshot_files)} 个文件")
    
    # 找出有对应截图的节点
    nodes = graph_data.get('nodes', {})
    valid_node_ids = set()
    removed_nodes = []
    
    for node_id, node_data in nodes.items():
        screen_path = node_data.get('screen_path', '')
        if screen_path in screenshot_files:
            valid_node_ids.add(node_id)
        else:
            removed_nodes.append({
                'node_id': node_id,
                'screen_path': screen_path,
                'url': node_data.get('url', '')
            })
    
    print(f"原始节点数: {len(nodes)}")
    print(f"有效节点数: {len(valid_node_ids)}")
    print(f"将移除的节点数: {len(removed_nodes)}")
    
    if removed_nodes:
        print("\n将移除的节点:")
        for node in removed_nodes[:10]:
            print(f"  - {node['node_id']}: {node['screen_path']}")
        if len(removed_nodes) > 10:
            print(f"  ... 还有 {len(removed_nodes) - 10} 个节点")
    
    # 过滤节点
    new_nodes = {
        node_id: node_data 
        for node_id, node_data in nodes.items() 
        if node_id in valid_node_ids
    }
    
    # 过滤边 - 只保留两端节点都有效的边
    edges = graph_data.get('edges', [])
    original_edge_count = len(edges)
    
    new_edges = [
        edge for edge in edges
        if edge.get('from_node_id') in valid_node_ids 
        and edge.get('to_node_id') in valid_node_ids
    ]
    
    print(f"\n原始边数: {original_edge_count}")
    print(f"保留的边数: {len(new_edges)}")
    print(f"移除的边数: {original_edge_count - len(new_edges)}")
    
    # 构建新的图数据
    new_graph_data = {
        'nodes': new_nodes,
        'edges': new_edges,
        'summary': {
            'total_nodes': len(new_nodes),
            'total_actions': len(new_edges),
            'total_edges': len(new_edges)
        }
    }
    
    # 写入输出文件
    if output_path is None:
        output_path = graph_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_graph_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n已保存清理后的图数据到: {output_path}")
    
    return {
        'original_nodes': len(nodes),
        'remaining_nodes': len(new_nodes),
        'removed_nodes': len(removed_nodes),
        'original_edges': original_edge_count,
        'remaining_edges': len(new_edges),
        'removed_edges': original_edge_count - len(new_edges)
    }


if __name__ == '__main__':
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    
    graph_path = script_dir / 'web_graph.json'
    screenshots_dir = script_dir / 'screenshots_cropped_resized'
    
    # 可以指定输出到新文件，避免覆盖原文件
    # output_path = script_dir / 'web_graph_cleaned.json'
    output_path = None  # 直接覆盖原文件
    
    result = clean_graph(
        str(graph_path),
        str(screenshots_dir),
        str(output_path) if output_path else None
    )
    
    print("\n=== 清理完成 ===")
    print(f"节点: {result['original_nodes']} -> {result['remaining_nodes']} (移除 {result['removed_nodes']})")
    print(f"边: {result['original_edges']} -> {result['remaining_edges']} (移除 {result['removed_edges']})")
