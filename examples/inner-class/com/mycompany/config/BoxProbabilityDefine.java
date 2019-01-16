package com.mycompany.config;

import java.util.*;


// 
public class BoxProbabilityDefine
{
    public class ProbabilityGoodsDefine 
    {
        public String GoodsID = "";       // 物品1id
        public int Num = 0;            // 物品1数量
        public int Probability = 0;    // 物品1概率
    };

    public String                             ID = "";             // ID
    public int                                Total = 0;           // 奖励总数
    public int                                Time = 0;            // 冷却时间
    public boolean                            Repeat = false;      // 是否可重复
    public ArrayList<ProbabilityGoodsDefine> ProbabilityGoods = new ArrayList<ProbabilityGoodsDefine>(); 

    private static ArrayList<BoxProbabilityDefine> data_;
    public static ArrayList<BoxProbabilityDefine> getData() { return data_; } 

    // parse fields data from text row
    public void parseFromRow(String[] row)
    {
        if (row.length < 13) {
            throw new RuntimeException(String.format("BoxProbabilityDefine: row length out of index %d", row.length));
        }
        if (!row[0].isEmpty()) {
            this.ID = row[0].trim();
        }
        if (!row[1].isEmpty()) {
            this.Total = Integer.parseInt(row[1]);
        }
        if (!row[2].isEmpty()) {
            this.Time = Integer.parseInt(row[2]);
        }
        if (!row[3].isEmpty()) {
            this.Repeat = Boolean.parseBoolean(row[3]);
        }
        for (int i = 4; i < 13; i += 3) 
        {
            ProbabilityGoodsDefine item = new ProbabilityGoodsDefine();
            if (!row[i + 0].isEmpty()) 
            {
                item.GoodsID = row[i + 0].trim();
            }
            if (!row[i + 1].isEmpty()) 
            {
                item.Num = Integer.parseInt(row[i + 1]);
            }
            if (!row[i + 2].isEmpty()) 
            {
                item.Probability = Integer.parseInt(row[i + 2]);
            }
            this.ProbabilityGoods.add(item);
        }
    }

    public static void loadFromFile(String filepath)
    {
        String[] lines = AutogenConfigManager.readFileToTextLines(filepath);
        data_ = new ArrayList<BoxProbabilityDefine>();
        for(String line : lines)
        {
            String[] row = line.split("\\,", -1);
            BoxProbabilityDefine obj = new BoxProbabilityDefine();
            obj.parseFromRow(row);
            data_.add(obj);
        }
    }

    // get an item by key
    public static BoxProbabilityDefine getItemBy(String ID)
    {
        for (BoxProbabilityDefine item : data_)
        {
            if (item.ID.equals(ID))
            {
                return item;
            }
        }
        return null;
    }

}
